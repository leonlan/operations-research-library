from docplex.cp import model as docp


def parallelmachinemodel(instance, mdl):
    """
    tasks = [[]] * instance.n
    for j in range(instance.n):
        tasks[j] = [mdl.interval_var(name="A_{}_{}".format(j,i), optional=True, size=instance.p[j][i]) for i in range(instance.g)]  #interval variable

    _tasks = [[]] * instance.n
    for j in range(instance.n):
        _tasks[j] = mdl.interval_var(name="T_{}".format(j))
    for j in range(instance.n):
            mdl.add(mdl.alternative(_tasks[j], [tasks[j][i] for i in range(instance.g)]))

    for i in range(instance.g):
        mdl.add(mdl.no_overlap( [tasks[j][i] for j in range(instance.n)]))     #no overlap machines

    mdl.add(mdl.minimize( mdl.max([ mdl.end_of(_tasks[j]) for j in range(instance.n) ]) ))   #this is makespan

    return mdl
    """

    machine = [
        mdl.integer_var(min=0, max=instance.g - 1) for j in range(instance.n)
    ]
    duration = [
        mdl.element(instance.p[j], machine[j]) for j in range(instance.n)
    ]  # duration[i] = matrix[i][machine[i]]
    makespan = max(
        [
            sum(
                [
                    instance.p[j][i] * (machine[j] == i)
                    for j in range(instance.n)
                ]
            )
            for i in range(instance.g)
        ]
    )
    mdl.add(
        sum([duration[j] for j in range(instance.n)]) <= instance.g * makespan
    )  # Mostly for strengthening lower bound
    mdl.add(docp.minimize(makespan))

    return mdl
