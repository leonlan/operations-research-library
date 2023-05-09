from .constraints import add_task_interval_variables


def Distributedflowshopmodel(data, mdl):
    jobs = range(data.num_jobs)
    stages = range(data.num_machines)
    factories = range(data.num_factories)

    tasks = [[] for _ in jobs]
    for j in jobs:
        tasks[j] = [[] for _ in stages]

    for j in jobs:
        for i in stages:
            tasks[j][i] = [
                mdl.interval_var(
                    name=f"A_{j}_{i}_{k}",
                    optional=True,
                    size=data.processing[j][i],
                )
                for k in factories
            ]

    _tasks = add_task_interval_variables(data, mdl)

    for j in jobs:
        for i in stages:
            subexpr = [tasks[j][i][k] for k in factories]
            expr = mdl.alternative(_tasks[j][i], subexpr)
            mdl.add(expr)

    for j in jobs:
        for i in range(1, data.num_machines):
            for k in factories:
                lhs = mdl.presence_of(tasks[j][i][k])
                rhs = mdl.presence_of(tasks[j][0][k])
                mdl.add(lhs >= rhs)

    seq_var = [[]] * data.num_machines
    for i in stages:
        seq_var[i] = [[]] * data.num_factories
        for k in factories:
            seq_var[i][k] = mdl.sequence_var([tasks[j][i][k] for j in jobs])

    for i in stages:
        for k in factories:
            mdl.add(mdl.no_overlap(seq_var[i][k]))  # no overlap machines

    for i in range(data.num_machines - 1):
        for k in factories:
            mdl.add(mdl.same_sequence(seq_var[i][k], seq_var[i + 1][k]))

    for j in jobs:
        for i in range(1, data.num_machines):
            mdl.add(mdl.end_before_start(_tasks[j][i - 1], _tasks[j][i]))

    makespan = mdl.max(
        [mdl.end_of(_tasks[j][data.num_machines - 1]) for j in jobs]
    )
    mdl.add(mdl.minimize(makespan))

    return mdl
