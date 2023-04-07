def Distributedflowshopmodel(data, mdl):
    tasks = [[] for j in range(data.n)]
    for j in range(data.n):
        tasks[j] = [[] for i in range(data.g)]

    for j in range(data.n):
        for i in range(data.g):
            tasks[j][i] = [
                mdl.interval_var(
                    name="A_{}_{}_{}".format(j, i, k),
                    optional=True,
                    size=data.p[j][i],
                )
                for k in range(data.f)
            ]  # interval variable

    _tasks = [[] for j in range(data.n)]
    for j in range(data.n):
        _tasks[j] = [
            mdl.interval_var(name="T_{}_{}".format(j, i))
            for i in range(data.g)
        ]
    for j in range(data.n):
        for i in range(data.g):
            # if i == 0:
            mdl.add(
                mdl.alternative(
                    _tasks[j][i], [tasks[j][i][k] for k in range(data.f)]
                )
            )

    for j in range(data.n):
        for i in range(1, data.g):
            for k in range(data.f):
                mdl.add(
                    mdl.presence_of(tasks[j][i][k])
                    >= mdl.presence_of(tasks[j][0][k])
                )

    Sequence_variable = [[]] * data.g
    for i in range(data.g):
        Sequence_variable[i] = [[]] * data.f
        for k in range(data.f):
            Sequence_variable[i][k] = mdl.sequence_var(
                [tasks[j][i][k] for j in range(data.n)]
            )

    for i in range(data.g):
        for k in range(data.f):
            mdl.add(
                mdl.no_overlap(Sequence_variable[i][k])
            )  # no overlap machines

    for i in range(data.g - 1):
        for k in range(data.f):
            mdl.add(
                mdl.same_sequence(
                    Sequence_variable[i][k], Sequence_variable[i + 1][k]
                )
            )

    # for i in range(data.g):
    #    for k in range(data.f):
    #        mdl.add(mdl.no_overlap( [tasks[j][i][k] for j in range(data.n)] ))     #no overlap machines

    for j in range(data.n):
        for i in range(1, data.g):
            mdl.add(
                mdl.end_before_start(_tasks[j][i - 1], _tasks[j][i])
            )  # no overlap jobs

    # for j in range(data.n):
    #    for i in range(1,data.g):
    #        for k in range(data.f):
    #            mdl.add(mdl.end_before_start(tasks[j][i-1][k],tasks[j][i][k]))     #no overlap jobs

    mdl.add(
        mdl.minimize(
            mdl.max([mdl.end_of(_tasks[j][data.g - 1]) for j in range(data.n)])
        )
    )  # this is makespan

    return mdl
