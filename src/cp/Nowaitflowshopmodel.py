def Nowaitflowshopmodel(data, mdl):
    tasks = [[]] * data.n
    for j in range(data.n):
        tasks[j] = [[]] * data.g

    for j in range(data.n):
        for i in range(data.g):
            tasks[j][i] = mdl.interval_var(
                name="T_{}_{}".format(j, i), size=data.p[j][i]
            )  # interval variable

    for i in range(data.g):
        mdl.add(
            mdl.no_overlap([tasks[j][i] for j in range(data.n)])
        )  # no overlap machines

    for j in range(data.n):
        for i in range(1, data.g):
            mdl.add(
                mdl.end_at_start(tasks[j][i - 1], tasks[j][i])
            )  # no overlap jobs

    Sequence_variable = [[]] * data.g
    for i in range(data.g):
        Sequence_variable[i] = mdl.sequence_var(
            [tasks[j][i] for j in range(data.n)]
        )

    for i in range(data.g - 1):
        mdl.add(
            mdl.same_sequence(Sequence_variable[i], Sequence_variable[i + 1])
        )

    mdl.add(
        mdl.minimize(
            mdl.max([mdl.end_of(tasks[j][data.g - 1]) for j in range(data.n)])
        )
    )  # this is makespan

    return mdl
