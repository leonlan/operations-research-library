import argparse
from itertools import combinations
from pathlib import Path

import docplex.cp.model as docp
import numpy as np

# from cp.constraints import add_task_interval_variables
# from cp.constraints.add_sequence_variables import add_sequence_variables
# from cp.constraints.all_machines_same_sequence import (
#     all_machines_same_sequence,
# )
# from cp.constraints.no_overlap_jobs import no_overlap_jobs
# from cp.constraints.no_overlap_machines import no_overlap_machines
from gurobipy import GRB, Model

M = 1000000
V = 1000000


class ProblemData:
    """
    Problem data for the permutation flow shop problem.
    """

    def __init__(self, processing_times: np.ndarray):
        self._processing_times = processing_times

        self._num_jobs = processing_times.shape[0]
        self._num_machines = processing_times.shape[1]

    @property
    def processing_times(self):
        return self._processing_times

    @property
    def num_jobs(self):
        return self._num_jobs

    @property
    def num_machines(self):
        return self._num_machines


def create_model(data):
    m = Model("Permutation flow shop")

    jobs = list(range(data.num_jobs))
    job_pairs = list(combinations(jobs, 2))  # (j, k) such that j < k

    # Variables
    x = m.addVars(job_pairs, vtype=GRB.BINARY, name="Job ordering")

    C = m.addVars(
        [(j, i) for j in jobs for i in range(data.num_machines)],
        vtype=GRB.CONTINUOUS,
        lb=0,
        ub=V,
        name="Completion time",
    )
    makespan = m.addVar(lb=0, ub=V, vtype=GRB.CONTINUOUS, name="Makespan")

    m.setObjective(makespan, GRB.MINIMIZE)

    # Constraint 1
    for j in jobs:
        m.addConstr(C[j, 0] >= data.processing_times[j][0])

    # Constraint 2
    for j in jobs:
        for i in range(1, data.num_machines):
            m.addConstr(C[j, i] - C[j, i - 1] >= data.processing_times[j][i])

    # Constraint 3 and 4
    for j in range(data.num_jobs - 1):
        for k in range(j + 1, data.num_jobs):
            for i in range(data.num_machines):
                expr1 = C[j, i] - C[k, i] + M * x[j, k]
                m.addConstr(expr1 >= data.processing_times[j][i] - M)

                expr2 = C[k, i] - C[j, i] - M * (1 - x[j, k])
                m.addConstr(expr2 >= data.processing_times[k][i])

    # Constraint 5
    for j in range(data.num_jobs):
        m.addConstr(makespan - C[j, data.num_machines - 1] >= 0)

    return m


def cp_model(data: ProblemData) -> docp.CpoModel:
    m = docp.CpoModel()

    tasks = add_task_interval_variables(data, m)
    no_overlap_jobs(data, m, tasks)

    machine_sequence = add_sequence_variables(data, m, tasks)
    no_overlap_machines(data, machine_sequence, m)
    all_machines_same_sequence(data, machine_sequence, m)

    return m


def main(instance: Path, model: str, time_limit: int):
    with open(instance, "r") as fh:
        lines = fh.readlines()

    processing_times = np.genfromtxt(lines[2:], delimiter=" ")
    data = ProblemData(processing_times)

    if model == "cp":
        mdl = cp_model(data)
        mdl.set_time_limit(time_limit)
        mdl.solve()
    if model == "mip":
        mdl = create_model(data)
        mdl.setParam("TimeLimit", time_limit)
        mdl.optimize()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("instance", type=Path, help="Path to instance file")
    parser.add_argument(
        "--model",
        type=str,
        help="Model to use",
        choices=["cp", "mip"],
        required=True,
    )
    parser.add_argument(
        "--time_limit",
        type=int,
        default=10,
        help="Solver time limit in seconds",
    )
    main(**vars(parser.parse_args()))
