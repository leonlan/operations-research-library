def Tardinessflowshopmodel(instance, mdl):
    tasks = [[]] * instance.n
    for j in range(instance.n):
        tasks[j] = [[]] * instance.g

    for j in range(instance.n):
        for i in range(instance.g):
            tasks[j][i] = mdl.interval_var(
                name="T_{}_{}".format(j, i), size=instance.p[j][i]
            )  # interval variable

    # for i in range(instance.g):
    #    mdl.add(mdl.no_overlap( [tasks[j][i] for j in range(instance.n)]))     #no overlap machines

    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.add(
                mdl.end_before_start(tasks[j][i - 1], tasks[j][i])
            )  # no overlap jobs

    Sequence_variable = [[]] * instance.g
    for i in range(instance.g):
        Sequence_variable[i] = mdl.sequence_var(
            [tasks[j][i] for j in range(instance.n)]
        )

    for i in range(instance.g):
        mdl.add(mdl.no_overlap(Sequence_variable[i]))  # no overlap machines

    for i in range(instance.g - 1):
        mdl.add(
            mdl.same_sequence(Sequence_variable[i], Sequence_variable[i + 1])
        )

    mdl.add(
        mdl.minimize(
            mdl.sum(
                [
                    mdl.max(
                        [
                            mdl.end_of(tasks[j][instance.g - 1])
                            - instance.d[j],
                            0,
                        ]
                    )
                    for j in range(instance.n)
                ]
            )
        )
    )  # this is total tardiness

    return mdl
