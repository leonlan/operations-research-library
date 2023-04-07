from .constants import V


def parallelmachinemodel(instance, mdl):
    # Variable Y
    names = [
        "Y_{}_{}".format(j, i)
        for j in range(instance.n)
        for i in range(instance.g)
    ]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)

    # Variable Cmax
    names += ["C_max"]
    objective += [1]
    lower_bounds += [0]
    upper_bounds += [V]
    types += ["C"]

    constraints = []
    senses = []
    rhs = []

    # constarint 1
    for j in range(instance.n):
        variables = ["Y_{}_{}".format(j, i) for i in range(instance.g)]
        coffiecient = [1] * instance.g
        constraints.append([variables, coffiecient])
        senses.append("E")
        rhs.append(1)

    # constarint 2
    for i in range(instance.g):
        variables = ["C_max"]
        coffiecient = [1]
        variables += ["Y_{}_{}".format(j, i) for j in range(instance.n)]
        coffiecient += [-1 * instance.p[j][i] for j in range(instance.n)]
        constraints.append([variables, coffiecient])
        senses.append("G")
        rhs.append(0)

    mdl.variables.add(
        obj=objective,
        lb=lower_bounds,
        ub=upper_bounds,
        names=names,
        types=types,
    )
    mdl.linear_constraints.add(lin_expr=constraints, senses=senses, rhs=rhs)
    mdl.objective.set_sense(mdl.objective.sense.minimize)
    return mdl
