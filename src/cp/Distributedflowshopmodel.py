def Distributedflowshopmodel(instance, mdl):
    tasks = [[] for j in range(instance.n)]
    for j in range(instance.n):
        tasks[j] = [[] for i in range(instance.g)]

    for j in range(instance.n):
        for i in range(instance.g):
            tasks[j][i] = [
                mdl.interval_var(
                    name="A_{}_{}_{}".format(j, i, k),
                    optional=True,
                    size=instance.p[j][i],
                )
                for k in range(instance.f)
            ]  # interval variable

    _tasks = [[] for j in range(instance.n)]
    for j in range(instance.n):
        _tasks[j] = [
            mdl.interval_var(name="T_{}_{}".format(j, i))
            for i in range(instance.g)
        ]
    for j in range(instance.n):
        for i in range(instance.g):
            # if i == 0:
            mdl.add(
                mdl.alternative(
                    _tasks[j][i], [tasks[j][i][k] for k in range(instance.f)]
                )
            )

    for j in range(instance.n):
        for i in range(1, instance.g):
            for k in range(instance.f):
                mdl.add(
                    mdl.presence_of(tasks[j][i][k])
                    >= mdl.presence_of(tasks[j][0][k])
                )

    Sequence_variable = [[]] * instance.g
    for i in range(instance.g):
        Sequence_variable[i] = [[]] * instance.f
        for k in range(instance.f):
            Sequence_variable[i][k] = mdl.sequence_var(
                [tasks[j][i][k] for j in range(instance.n)]
            )

    for i in range(instance.g):
        for k in range(instance.f):
            mdl.add(
                mdl.no_overlap(Sequence_variable[i][k])
            )  # no overlap machines

    for i in range(instance.g - 1):
        for k in range(instance.f):
            mdl.add(
                mdl.same_sequence(
                    Sequence_variable[i][k], Sequence_variable[i + 1][k]
                )
            )

    # for i in range(instance.g):
    #    for k in range(instance.f):
    #        mdl.add(mdl.no_overlap( [tasks[j][i][k] for j in range(instance.n)] ))     #no overlap machines

    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.add(
                mdl.end_before_start(_tasks[j][i - 1], _tasks[j][i])
            )  # no overlap jobs

    # for j in range(instance.n):
    #    for i in range(1,instance.g):
    #        for k in range(instance.f):
    #            mdl.add(mdl.end_before_start(tasks[j][i-1][k],tasks[j][i][k]))     #no overlap jobs

    mdl.add(
        mdl.minimize(
            mdl.max(
                [
                    mdl.end_of(_tasks[j][instance.g - 1])
                    for j in range(instance.n)
                ]
            )
        )
    )  # this is makespan

    return mdl
