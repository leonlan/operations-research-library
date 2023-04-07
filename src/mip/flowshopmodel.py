from .constants import M, V


def flowshopmodel(instance, mdl):
    # Variable X
    names = [
        "X_{}_{}".format(j, j1)
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
    ]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)
    # Variable C
    names += [
        "C_{}_{}".format(j, i)
        for j in range(instance.n)
        for i in range(instance.g)
    ]
    objective += [0] * instance.n * instance.g
    lower_bounds += [0] * instance.n * instance.g
    upper_bounds += [V] * instance.n * instance.g
    types += ["C"] * instance.n * instance.g

    # Variable Cmax
    names += ["C_max"]
    objective += [1]
    lower_bounds += [0]
    upper_bounds += [V]
    types += ["C"]

    ###### Constarints ########
    constraints = []
    senses = []
    rhs = []

    # constarint 1
    for j in range(instance.n):
        variables = ["C_{}_{}".format(j, 0)]
        coffiecient = [1]
        constraints.append([variables, coffiecient])
        senses.append("G")
        rhs.append(instance.p[j][0])

    # constarint 2
    for j in range(instance.n):
        for i in range(1, instance.g):
            variables = ["C_{}_{}".format(j, i)]
            variables += ["C_{}_{}".format(j, i - 1)]
            coffiecient = [1, -1]
            constraints.append([variables, coffiecient])
            senses.append("G")
            rhs.append(instance.p[j][i])

    # constarint 3
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                variables = ["C_{}_{}".format(j, i)]
                variables += ["C_{}_{}".format(j1, i)]
                variables += ["X_{}_{}".format(j, j1)]
                coffiecient = [1, -1, -M]
                constraints.append([variables, coffiecient])
                senses.append("G")
                rhs.append(instance.p[j][i] - M)

    # constarint 4
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                variables = ["C_{}_{}".format(j1, i)]
                variables += ["C_{}_{}".format(j, i)]
                variables += ["X_{}_{}".format(j, j1)]
                coffiecient = [1, -1, M]
                constraints.append([variables, coffiecient])
                senses.append("G")
                rhs.append(instance.p[j1][i])

    # constarint 5
    for j in range(instance.n):
        variables = ["C_max"]
        variables += ["C_{}_{}".format(j, instance.g - 1)]
        coffiecient = [1, -1]
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
