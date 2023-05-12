import random
from itertools import product

import docplex.cp.model as docp
import numpy as np

from .constraints.add_task_interval_variables import (
    add_task_interval_variables,
)
from .constraints.minimize_makespan import minimize_makespan
from .constraints.no_overlap_jobs import no_overlap_jobs

random.seed(0)


def HybridFlowShop(data, model="explicit"):
    return (
        HybridFlowShopPulse(data)
        if model == "pulse"
        else HybridFlowShopExplicit(data)
    )


def HybridFlowShopPulse(data):
    """
    Hybrid Flow Shop modeled with pulse constraints. This model assumes
    that there is one big supermachine for each set of identical machines
    per stage, which can process a number of jobs equal to the number of
    machines in the set. The pulse model "ignores" the assignment problem
    and only solves the sequencing problem constrained with resources.
    """
    mdl = docp.CpoModel()

    tasks = add_task_interval_variables(data, mdl)

    for i in range(data.num_machines):
        expr = [mdl.pulse(tasks[j][i], 1) for j in range(data.num_jobs)]
        mdl.add(mdl.sum(expr) <= data.machines[i])

    no_overlap_jobs(data, mdl, tasks)

    minimize_makespan(data, mdl, tasks)

    return mdl


def HybridFlowShopExplicit(data):
    """
    Hybrid Flow Shop modeled with explicit interval variables. This model
    explicitly solves a sequencing and assignment problem, where each job
    is assigned to a machine and the sequence of jobs on each machine is
    determined. This model is more complex than the pulse model.
    """
    mdl = docp.CpoModel()

    tasks = create_tasks_matrix(data, mdl)
    _tasks = add_task_interval_variables(data, mdl, include_processing=False)

    no_overlap_jobs(data, mdl, _tasks)
    add_alternative_constraints(data, mdl, tasks, _tasks)
    no_overlap_on_machines(data, mdl, tasks)

    minimize_makespan(data, mdl, _tasks)

    return mdl


def create_tasks_matrix(data, mdl):
    tasks = [
        [[] for _ in range(data.num_machines)] for _ in range(data.num_jobs)
    ]

    for j, i in product(range(data.num_jobs), range(data.num_machines)):
        tmp = []

        for k in range(data.machines[i]):
            is_eligible = random.randint(0, 5)  #  data.eligible[j][i][k]

            if not is_eligible:
                tmp.append(None)
            else:
                name = f"A_{j}_{i}_{k}"
                duration = data.processing[j][i]
                tmp.append(
                    mdl.interval_var(name=name, optional=True, size=duration)
                )

        tasks[j][i] = tmp

    return tasks


def add_alternative_constraints(data, mdl, tasks, _tasks):
    for j in range(data.num_jobs):
        for i in range(data.num_machines):
            assignment_vars = [x for x in tasks[j][i] if x is not None]
            mdl.add(mdl.alternative(_tasks[j][i], assignment_vars))


def no_overlap_on_machines(data, mdl, tasks):
    for i in range(data.num_machines):
        for k in range(data.machines[i]):
            # HACK: Dummy sequence setup times, because HFS has a different
            # problem data structure than other FS problems.
            setup = np.ones((data.num_jobs, data.num_jobs), dtype=int)
            seq_tasks = [tasks[j][i][k] for j in range(data.num_jobs)]
            seq_tasks = [x for x in seq_tasks if x is not None]

            cons = mdl.no_overlap(mdl.sequence_var(seq_tasks), setup)
            mdl.add(cons)
