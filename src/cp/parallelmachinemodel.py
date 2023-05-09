def parallelmachinemodel(data, mdl):
    """
    tasks = [[]] * data.n
    for j in range(data.n):
        tasks[j] = [mdl.interval_var(name="A_{}_{}".format(j,i), optional=True, size=data.p[j][i]) for i in range(data.g)]  #interval variable

    _tasks = [[]] * data.n
    for j in range(data.n):
        _tasks[j] = mdl.interval_var(name="T_{}".format(j))
    for j in range(data.n):
            mdl.add(mdl.alternative(_tasks[j], [tasks[j][i] for i in range(data.g)]))

    for i in range(data.g):
        mdl.add(mdl.no_overlap( [tasks[j][i] for j in range(data.n)]))     #no overlap machines

    mdl.add(mdl.minimize( mdl.max([ mdl.end_of(_tasks[j]) for j in range(data.n) ]) ))   #this is makespan

    return mdl
    """

    machine = [
        mdl.integer_var(min=0, max=data.num_machines - 1)
        for _ in range(data.num_jobs)
    ]
    duration = [
        mdl.element(data.processing[j], machine[j])
        for j in range(data.num_jobs)
    ]

    def load(i):
        return [
            data.processing[j][i] * (machine[j] == i)
            for j in range(data.num_jobs)
        ]

    makespan = max([sum(load(i)) for i in range(data.num_machines)])

    lhs = sum([duration[j] for j in range(data.num_jobs)])
    mdl.add(lhs <= data.num_machines * makespan)

    mdl.add(mdl.minimize(makespan))

    return mdl
