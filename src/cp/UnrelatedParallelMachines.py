from itertools import product

import docplex.cp.model as docp


def UnrelatedParallelMachines(data):
    """
    Unrelated Parallel Machines problem with sequence dependent setup times
    and machine eligibility constraints.
    """
    mdl = docp.CpoModel()

    # Variables
    tasks = [mdl.interval_var(name=f"T_{j}") for j in range(data.num_jobs)]
    assignments = [
        [
            mdl.interval_var(
                name=f"A_{j}_{i}", size=data.processing[j][i], optional=True
            )
            for i in range(data.num_machines)
        ]
        for j in range(data.num_jobs)
    ]
    sequences = [
        mdl.sequence_var([assignments[j][i] for j in range(data.num_jobs)])
        for i in range(data.num_machines)
    ]

    # Constraints
    assign_one_machine(data, mdl, tasks, assignments)
    no_overlap_machine(data, mdl, sequences)
    machine_eligibility(data, mdl, assignments)
    minimize_makespan(data, mdl, tasks)

    return mdl


def assign_one_machine(data, mdl, tasks, operations):
    """
    Each job is assigned to exactly one machine by implementing the following
    constraint:

        Alternative(T_j, [A_j_1, ..., A_j_m])
    """
    for j in range(data.num_jobs):
        cons = mdl.alternative(tasks[j], operations[j])
        mdl.add(cons)


def no_overlap_machine(data, mdl, sequences):
    """
    No overlap constraint for each machine, including sequence depdent setup
    times. The following constraint is implemented:

        NoOverlap(A_1, ..., A_n, setup_1, ..., setup_n)
    """
    for i in range(data.num_machines):
        cons = mdl.no_overlap(sequences[i], data.setup[i])
        mdl.add(cons)


def machine_eligibility(data, mdl, assignments):
    """
    Machine eligibility constraint. The following constraint is implemented:

        If machine i is not eligible for job j, then A_j_i is absent.
    """
    for job, machine in product(
        range(data.num_jobs), range(data.num_machines)
    ):
        if not data.eligible[job][machine]:
            cons = mdl.presence_of(assignments[job][machine]) == 0
            mdl.add(cons)


def minimize_makespan(data, mdl, tasks):
    makespan = mdl.max([mdl.end_of(tasks[j]) for j in range(data.num_jobs)])
    mdl.add(mdl.minimize(makespan))
