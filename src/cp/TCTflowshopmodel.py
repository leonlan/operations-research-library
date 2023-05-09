def TCTflowshopmodel(data, mdl):
    tasks = [[]] * data.jobs
    for j in range(data.jobs):
        tasks[j] = [[]] * data.machines

    for j in range(data.jobs):
        for i in range(data.machines):
            tasks[j][i] = mdl.interval_var(
                name="T_{}_{}".format(j, i), size=data.processing[j][i]
            )  # interval variable

    for j in range(data.jobs):
        for i in range(1, data.machines):
            mdl.add(
                mdl.end_before_start(tasks[j][i - 1], tasks[j][i])
            )  # no overlap jobs

    Sequence_variable = [[]] * data.machines
    for i in range(data.machines):
        Sequence_variable[i] = mdl.sequence_var(
            [tasks[j][i] for j in range(data.jobs)]
        )

    for i in range(data.machines):
        mdl.add(mdl.no_overlap(Sequence_variable[i]))  # no overlap machines

    for i in range(data.machines - 1):
        mdl.add(
            mdl.same_sequence(Sequence_variable[i], Sequence_variable[i + 1])
        )

    mdl.add(
        mdl.minimize(
            mdl.sum(
                [
                    mdl.end_of(tasks[j][data.machines - 1])
                    for j in range(data.jobs)
                ]
            )
        )
    )  # this is total tardiness

    return mdl
