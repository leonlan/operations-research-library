from itertools import product

import docplex.cp.model as docp

from .constraints.add_task_interval_variables import (
    create_task_interval_variables,
)
from .constraints.minimize_makespan import minimize_makespan
from .constraints.no_overlap_between_machines import (
    no_overlap_between_machines,
)


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
    model = docp.CpoModel()

    tasks = create_task_interval_variables(data, model)

    for s in data.stages:
        expr = [model.pulse(tasks[j][s], 1) for j in data.jobs]
        model.add(model.sum(expr) <= data.machines[s])

    no_overlap_between_machines(data, model, tasks)

    minimize_makespan(data, model, tasks)

    return model


def HybridFlowShopExplicit(data):
    """
    Hybrid Flow Shop modeled with explicit interval variables. This model
    explicitly solves a sequencing and assignment problem, where each job
    is assigned to a machine and the sequence of jobs on each machine is
    determined. This model is more complex than the pulse model, but it can
    model more complex hybrid flow shop problems.
    """
    model = docp.CpoModel()

    # Variables
    tasks = create_task_interval_variables(
        data, model, include_processing=False
    )
    assign = create_assignment_variables(data, model)

    # Constraints
    assign_one_machine_per_stage(data, model, assign, tasks)
    machine_eligibility(data, model, assign)

    no_overlap_between_machines(data, model, tasks)
    no_overlap_on_machines(data, model, assign)
    inter_stage_accessibility(data, model, assign)

    minimize_makespan(data, model, tasks)

    return model


def create_assignment_variables(data, model):
    """
    Creates interval variables for each (job, stage, machine). These are
    used for assignment constraints.
    """
    assign = {}

    for job, stage in product(data.jobs, data.stages):
        for machine in range(data.machines[stage]):
            name = f"A_{job}_{stage}_{machine}"
            size = data.processing[job][stage]
            assign[(job, stage, machine)] = model.interval_var(
                name=name, size=size, optional=True
            )

    return assign


def machine_eligibility(data, model, assign):
    """
    Implements the machine eligibility constraints on assignment variables.
    """
    for job, stage in product(data.jobs, data.stages):
        for machine in range(data.machines[stage]):
            if not data.eligible[job][stage][machine]:
                cons = model.presence_of(assign[(job, stage, machine)]) == 0
                model.add(cons)


def assign_one_machine_per_stage(data, model, assign, tasks):
    """
    Implements the constraint

        Alternative(Task[j][i], Task[j][i][k] for all k)

    for each (job, stage) pair.

    This constraint ensures that only one of the assignment interval variables
    is present at any time.
    """
    for job, stage in product(data.jobs, data.stages):
        machines = range(data.machines[stage])
        intervals = [assign[(job, stage, machine)] for machine in machines]
        cons = model.alternative(tasks[job][stage], intervals)
        model.add(cons)


def no_overlap_on_machines(data, model, assign):
    """
    Implements the no overlap constraints on assignment variables for a single
    machine. This constraint ensures that no two jobs are processed on the same
    machine at the same time.

        NoOverlap(Task[j][s][k] for all j, setup[:, :, s, k])
    """
    for stage in data.stages:
        for k in range(data.machines[stage]):
            setup = data.setup[:, :, stage, k]
            intervals = [assign[(j, stage, k)] for j in data.jobs]
            cons = model.no_overlap(model.sequence_var(intervals), setup)
            model.add(cons)


def inter_stage_accessibility(data, model, assign):
    """
    Accessibility constraints are constraints that ensure that a job can only
    be produced on stage $i$ line $l$ if it is accesible from the line $l'$
    that it was produced on in stage $i-1$, for $i > 0$.

    PresenceOf(assign[j][i][k])
       <= sum(PresenceOf(assign[j][i-1][k'] for k' in range(machines[i-1])))
    """
    for job, stage in product(data.jobs, range(1, data.num_stages)):
        for machine in range(data.machines[stage]):
            expr = model.sum(
                [
                    model.presence_of(assign[(job, stage - 1, machine_)])
                    for machine_ in range(data.machines[stage - 1])
                ]
            )
            cons = model.presence_of(assign[(job, stage, machine)]) <= expr
            model.add(cons)
