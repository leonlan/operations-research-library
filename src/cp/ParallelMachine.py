def ParallelMachine(data, model):
    """
    tasks = [[]] * data.n
    for j in range(data.n):
        tasks[j] = [model.interval_var(name="A_{}_{}".format(j,i), optional=True, size=data.p[j][i]) for i in range(data.g)]  #interval variable

    _tasks = [[]] * data.n
    for j in range(data.n):
        _tasks[j] = model.interval_var(name="T_{}".format(j))
    for j in range(data.n):
            model.add(model.alternative(_tasks[j], [tasks[j][i] for i in range(data.g)]))

    for i in range(data.g):
        model.add(model.no_overlap( [tasks[j][i] for j in range(data.n)]))     #no overlap machines

    model.add(model.minimize( model.max([ model.end_of(_tasks[j]) for j in range(data.n) ]) ))   #this is makespan

    return model
    """

    machine = [
        model.integer_var(min=0, max=data.num_machines - 1)
        for _ in range(data.num_jobs)
    ]
    duration = [
        model.element(data.processing[j], machine[j])
        for j in range(data.num_jobs)
    ]

    def load(i):
        return [
            data.processing[j][i] * (machine[j] == i)
            for j in range(data.num_jobs)
        ]

    makespan = max([sum(load(i)) for i in range(data.num_machines)])

    lhs = sum([duration[j] for j in range(data.num_jobs)])
    model.add(lhs <= data.num_machines * makespan)

    model.add(model.minimize(makespan))

    return model
