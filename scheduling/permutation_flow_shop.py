import docplex.cp.model as docp
import numpy as np
from cp.constraints import add_task_interval_variables
from cp.constraints.add_sequence_variables import add_sequence_variables
from cp.constraints.all_machines_same_sequence import (
    all_machines_same_sequence,
)
from cp.constraints.no_overlap_jobs import no_overlap_jobs
from cp.constraints.no_overlap_machines import no_overlap_machines
from gurobipy import Model

M = 1000000
V = 1000000


class ProblemData:
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


def mip_model(data: ProblemData):
    mdl = Model("Permutation flow shop")

    # Variable X
    names = [
        "X_{}_{}".format(j, j1)
        for j in range(data.num_jobs)
        for j1 in range(j + 1, data.num_jobs)
    ]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)
    # Variable C
    names += [
        "C_{}_{}".format(j, i)
        for j in range(data.num_jobs)
        for i in range(data.num_machines)
    ]
    objective += [0] * data.num_jobs * data.num_machines
    lower_bounds += [0] * data.num_jobs * data.num_machines
    upper_bounds += [V] * data.num_jobs * data.num_machines
    types += ["C"] * data.num_jobs * data.num_machines

    # Variable Cmax
    names += ["C_max"]
    objective += [1]
    lower_bounds += [0]
    upper_bounds += [V]
    types += ["C"]

    ###### constraints ########
    constraints = []
    senses = []
    rhs = []

    # constraint 1
    for j in range(data.num_jobs):
        variables = ["C_{}_{}".format(j, 0)]
        coffiecient = [1]
        constraints.append([variables, coffiecient])
        senses.append("G")
        rhs.append(data.processing_times[j][0])

    # constraint 2
    for j in range(data.num_jobs):
        for i in range(1, data.num_machines):
            variables = ["C_{}_{}".format(j, i)]
            variables += ["C_{}_{}".format(j, i - 1)]
            coffiecient = [1, -1]
            constraints.append([variables, coffiecient])
            senses.append("G")
            rhs.append(data.processing_times[j][i])

    # constraint 3
    for j in range(data.num_jobs - 1):
        for j1 in range(j + 1, data.num_jobs):
            for i in range(data.num_machines):
                variables = ["C_{}_{}".format(j, i)]
                variables += ["C_{}_{}".format(j1, i)]
                variables += ["X_{}_{}".format(j, j1)]
                coffiecient = [1, -1, -M]
                constraints.append([variables, coffiecient])
                senses.append("G")
                rhs.append(data.processing_times[j][i] - M)

    # constraint 4
    for j in range(data.num_jobs - 1):
        for j1 in range(j + 1, data.num_jobs):
            for i in range(data.num_machines):
                variables = ["C_{}_{}".format(j1, i)]
                variables += ["C_{}_{}".format(j, i)]
                variables += ["X_{}_{}".format(j, j1)]
                coffiecient = [1, -1, M]
                constraints.append([variables, coffiecient])
                senses.append("G")
                rhs.append(data.processing_times[j1][i])

    # constraint 5
    for j in range(data.num_jobs):
        variables = ["C_max"]
        variables += ["C_{}_{}".format(j, data.num_machines - 1)]
        coffiecient = [1, -1]
        constraints.append([variables, coffiecient])
        senses.append("G")
        rhs.append(0)

    mdl.variables.add(
        obj=objective,
        lb=lower_bounds,
        ub=upper_bounds,
        names=names,
        types=types,
    )
    mdl.linear_constraints.add(lin_expr=constraints, senses=senses, rhs=rhs)
    mdl.objective.set_sense(mdl.objective.sense.minimize)
    return mdl


def cp_model(data: ProblemData) -> docp.CpoModel:
    mdl = docp.CpoModel()

    tasks = add_task_interval_variables(data, mdl)
    no_overlap_jobs(data, mdl, tasks)

    machine_sequence = add_sequence_variables(data, mdl, tasks)
    no_overlap_machines(data, machine_sequence, mdl)
    all_machines_same_sequence(data, machine_sequence, mdl)

    return mdl
