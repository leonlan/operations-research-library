import docplex.cp.model as docp


def UnrelatedParallelMachines(data):
    """
    Unrelated Parallel Machines problem with sequence dependent setup times.
    """
    mdl = docp.CpoModel()

    # Variables
    tasks = [mdl.interval_var(name=f"T_{j}") for j in range(data.num_jobs)]
    operations = [
        [
            mdl.interval_var(
                name=f"O_{j}_{i}", size=data.processing[j][i], optional=True
            )
            for i in range(data.num_machines)
        ]
        for j in range(data.num_jobs)
    ]
    sequences = [
        mdl.sequence_var([operations[j][i] for j in range(data.num_jobs)])
        for i in range(data.num_machines)
    ]

    # Constraints
    select_one_operation(data, mdl, tasks, operations)
    no_overlap_machine(data, mdl, sequences)
    minimize_makespan(data, mdl, tasks)

    return mdl


def select_one_operation(data, mdl, tasks, operations):
    for j in range(data.num_jobs):
        cons = mdl.alternative(tasks[j], operations[j])
        mdl.add(cons)


def minimize_makespan(data, mdl, tasks):
    makespan = mdl.max([mdl.end_of(tasks[j]) for j in range(data.num_jobs)])
    mdl.add(mdl.minimize(makespan))


def no_overlap_machine(data, mdl, sequences):
    for i in range(data.num_machines):
        cons = mdl.no_overlap(sequences[i], data.setup[i])
        mdl.add(cons)
