from itertools import product

import docplex.cp.model as docp


def UnrelatedParallelMachines(data):
    """
    Unrelated Parallel Machines problem with sequence dependent setup times
    and machine eligibility constraints.
    """
    model = docp.CpoModel()

    # Variables
    tasks = {
        j: model.interval_var(name=f"T_{j}") for j in range(data.num_jobs)
    }
    assign = {
        (j, i): model.interval_var(
            name=f"A_{j}_{i}", size=data.processing[j][i], optional=True
        )
        for i, j in product(range(data.num_machines), range(data.num_jobs))
    }
    sequences = {
        i: model.sequence_var([assign[(j, i)] for j in range(data.num_jobs)])
        for i in range(data.num_machines)
    }

    assign_job_to_one_machine(data, model, tasks, assign)
    no_overlap_machine(data, model, sequences)
    machine_eligibility(data, model, assign)
    minimize_makespan(data, model, tasks)

    return model


def assign_job_to_one_machine(data, model, tasks, operations):
    """
    Each job is assigned to exactly one machine by implementing the following
    constraint:

        Alternative(T_j, [A_j_1, ..., A_j_m])
    """
    for j in range(data.num_jobs):
        cons = model.alternative(tasks[j], operations[j])
        model.add(cons)


def no_overlap_machine(data, model, sequences):
    """
    No overlap constraint for each machine, including sequence depdent setup
    times. The following constraint is implemented:

        NoOverlap(A_1, ..., A_n, setup_1, ..., setup_n)
    """
    for i in range(data.num_machines):
        cons = model.no_overlap(sequences[i], data.setup[i])
        model.add(cons)


def machine_eligibility(data, model, assignments):
    """
    Machine eligibility constraint. The following constraint is implemented:

        If machine i is not eligible for job j, then A_j_i is absent.
    """
    for job, machine in product(
        range(data.num_jobs), range(data.num_machines)
    ):
        if not data.eligible[job][machine]:
            cons = model.presence_of(assignments[(job, machine)]) == 0
            model.add(cons)


def minimize_makespan(data, model, tasks):
    makespan = model.max(
        [model.end_of(tasks[j]) for j in range(data.num_jobs)]
    )
    model.add(model.minimize(makespan))
