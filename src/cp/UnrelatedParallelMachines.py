from itertools import product

import docplex.cp.model as docp


def UnrelatedParallelMachines(data):
    """
    Unrelated Parallel Machines problem with sequence dependent setup times
    and machine eligibility constraints.
    """
    model = docp.CpoModel()

    # Variables
    tasks = model.interval_var_dict(list(data.jobs), name="T")
    assign = create_assignment_variables(data, model)

    assign_job_to_one_machine(data, model, tasks, assign)
    no_overlap_machine(data, model, assign)
    machine_eligibility(data, model, assign)
    minimize_makespan(data, model, tasks)

    return model


def create_assignment_variables(data, model):
    assign = {}

    for j, i in product(data.jobs, data.machines):
        name = f"A_{j}_{i}"
        size = data.processing[j][i]
        assign[(j, i)] = model.interval_var(
            name=name, size=size, optional=True
        )

    return assign


def assign_job_to_one_machine(data, model, tasks, assign):
    """
    Each job is assigned to exactly one machine by implementing the following
    constraint:

        Alternative(T_j, [A_j_1, ..., A_j_m])
    """
    for j in data.jobs:
        intervals = [assign[(j, i)] for i in data.machines]
        cons = model.alternative(tasks[j], intervals)
        model.add(cons)


def no_overlap_machine(data, model, assign):
    """
    No overlap constraint for each machine, including sequence dependent setup
    times. The following constraint is implemented:

        NoOverlap(A_1, ..., A_n, setup_1, ..., setup_n)
    """
    for i in data.machines:
        sequence = model.sequence_var([assign[(j, i)] for j in data.jobs])
        cons = model.no_overlap(sequence, data.setup[i])
        model.add(cons)


def machine_eligibility(data, model, assignments):
    """
    Machine eligibility constraint. The following constraint is implemented:

        If machine i is not eligible for job j, then A_j_i is absent.
    """
    for job, machine in product(data.jobs, data.machines):
        if not data.eligible[job][machine]:
            cons = model.presence_of(assignments[(job, machine)]) == 0
            model.add(cons)


def minimize_makespan(data, model, tasks):
    makespan = model.max([model.end_of(tasks[j]) for j in data.jobs])
    model.add(model.minimize(makespan))
