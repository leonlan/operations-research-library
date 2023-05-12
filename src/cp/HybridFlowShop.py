import docplex.cp.model as docp

from .constraints.add_task_interval_variables import (
    add_task_interval_variables,
)
from .constraints.minimize_makespan import minimize_makespan
from .constraints.no_overlap_jobs import no_overlap_jobs


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
    enforce_no_overlap_jobs(data, mdl, tasks)

    minimize_makespan(data, mdl, _tasks)

    return mdl


def create_tasks_matrix(data, mdl):
    tasks = [[]] * data.num_jobs

    for j in range(data.num_jobs):
        tasks[j] = [[]] * data.num_machines

    for j in range(data.num_jobs):
        for i in range(data.num_machines):
            tasks[j][i] = [
                mdl.interval_var(
                    name=f"A_{j}_{i}_{k}",
                    optional=True,
                    size=data.processing[j][i],
                )
                for k in range(data.machines[i])
            ]
    return tasks


def add_alternative_constraints(data, mdl, tasks, _tasks):
    for j in range(data.num_jobs):
        for i in range(data.num_machines):
            mdl.add(
                mdl.alternative(
                    _tasks[j][i],
                    [tasks[j][i][k] for k in range(data.machines[i])],
                )
            )


def enforce_no_overlap_jobs(data, mdl, tasks):
    for i in range(data.num_machines):
        for k in range(data.machines[i]):
            mdl.add(
                mdl.no_overlap([tasks[j][i][k] for j in range(data.num_jobs)])
            )
