import random
from itertools import product

import docplex.cp.model as docp
import numpy.random as rnd

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

    for i in range(data.num_stages):
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

    # _tasks are interval variables for each (job, stage) pair to be used
    # for sequencing constraints.
    _tasks = add_task_interval_variables(data, mdl, include_processing=False)
    no_overlap_jobs(data, mdl, _tasks)

    # tasks are interval variables for each (job, stage, machine) triple
    # to be used for assignment constraints.
    tasks = create_tasks_matrix(data, mdl)
    assign_one_machine_per_stage(data, mdl, tasks, _tasks)
    machine_eligibility(data, mdl, tasks)
    no_overlap_on_machines(data, mdl, tasks)
    inter_stage_accessibility(data, mdl, tasks)

    minimize_makespan(data, mdl, _tasks)

    return mdl


def create_tasks_matrix(data, mdl):
    """
    Creates interval variables for each (job, stage, machine). These are
    used for assignment constraints.
    """
    tasks = [
        [
            [[] for _ in range(data.machines[stage])]
            for stage in range(data.num_stages)
        ]
        for _ in range(data.num_jobs)
    ]

    for j, i in product(range(data.num_jobs), range(data.num_stages)):
        for k in range(data.machines[i]):
            name = f"A_{j}_{i}_{k}"
            duration = data.processing[j][i]
            tasks[j][i][k] = mdl.interval_var(
                name=name, optional=True, size=duration
            )

    return tasks


def machine_eligibility(data, mdl, tasks):
    """
    Implements the machine eligibility constraints on assignment variables.
    """
    for job, stage in product(range(data.num_jobs), range(data.num_stages)):
        for machine in range(data.machines[stage]):
            if not random.randint(0, 5):  # TODO change to data
                cons = mdl.presence_of(tasks[job][stage][machine]) == 0
                mdl.add(cons)


def assign_one_machine_per_stage(data, mdl, tasks, _tasks):
    """
    Implements the constraint

        Alternative(Task[j][i], Task[j][i][k] for all k)

    for each (job, stage) pair.

    This constraint ensures that only one of the assignment interval variables
    is present at any time.
    """
    for job, stage in product(range(data.num_jobs), range(data.num_stages)):
        cons = mdl.alternative(_tasks[job][stage], tasks[job][stage])
        mdl.add(cons)


def no_overlap_on_machines(data, mdl, tasks):
    """
    Implements the no overlap constraints on assignment variables for a single
    machine. This constraint ensures that no two jobs are processed on the same
    machine at the same time.

    Setup times are currently randomly generated.
    """
    for i in range(data.num_stages):
        for k in range(data.machines[i]):
            # TODO Infer setup times from data
            setup = rnd.randint(0, 100, (data.num_jobs, data.num_jobs))
            seq_tasks = [tasks[j][i][k] for j in range(data.num_jobs)]

            cons = mdl.no_overlap(mdl.sequence_var(seq_tasks), setup)
            mdl.add(cons)


def inter_stage_accessibility(data, mdl, tasks):
    """
    Accessibility constraints are constraints that ensure that a job can only
    be produced on stage $i$ line $l$ if it is accesible from the line $l'$
    that it was produced on in stage $i-1$, for $i > 0$.
    """
    for job, stage in product(range(data.num_jobs), range(1, data.num_stages)):
        for k in range(data.machines[stage]):
            can_access_k = mdl.sum(
                [
                    mdl.presence_of(tasks[job][stage - 1][k_])
                    for k_ in range(data.machines[stage - 1])
                ]
            )
            cons = can_access_k >= mdl.presence_of(tasks[job][stage][k])
            mdl.add(cons)
