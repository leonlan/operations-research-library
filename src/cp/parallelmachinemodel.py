from docplex.cp import model as docp


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

    machine = [mdl.integer_var(min=0, max=data.g - 1) for _ in range(data.n)]
    duration = [mdl.element(data.p[j], machine[j]) for j in range(data.n)]

    makespan = max(
        [
            sum([data.p[j][i] * (machine[j] == i) for j in range(data.n)])
            for i in range(data.g)
        ]
    )

    lhs = sum([duration[j] for j in range(data.n)])
    mdl.add(lhs <= data.g * makespan)

    mdl.add(docp.minimize(makespan))

    return mdl
