# TODO


def Hybridflowshopmodel(instance, mdl):
    # Variable Y
    names = [
        "Y_{}_{}_{}".format(j, i, k)
        for j in range(instance.n)
        for i in range(instance.g)
        for k in range(instance.m[i])
    ]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)

    # Variable X
    names += [
        "X_{}_{}_{}".format(j, j1, i)
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
        for i in range(instance.g)
    ]
    objective += [
        0
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
        for i in range(instance.g)
    ]
    lower_bounds += [
        0
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
        for i in range(instance.g)
    ]
    upper_bounds += [
        1
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
        for i in range(instance.g)
    ]
    types += [
        "B"
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
        for i in range(instance.g)
    ]

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

    constraints = []
    senses = []
    rhs = []

    # constarint 1
    for j in range(instance.n):
        for i in range(instance.g):
            variables = [
                "Y_{}_{}_{}".format(j, i, k) for k in range(instance.m[i])
            ]
            coffiecient = [1] * instance.m[i]
            constraints.append([variables, coffiecient])
            senses.append("E")
            rhs.append(1)

    # constarint 2-1
    for j in range(instance.n):
        variables = ["C_{}_{}".format(j, 0)]
        coffiecient = [1]
        constraints.append([variables, coffiecient])
        senses.append("G")
        rhs.append(instance.p[j][0])

    # constarint 2-2
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
                for k in range(instance.m[i]):
                    variables = ["C_{}_{}".format(j, i)]
                    variables += ["C_{}_{}".format(j1, i)]
                    variables += ["X_{}_{}_{}".format(j, j1, i)]
                    variables += ["Y_{}_{}_{}".format(j, i, k)]
                    variables += ["Y_{}_{}_{}".format(j1, i, k)]
                    coffiecient = [1, -1, -M, -M, -M]
                    constraints.append([variables, coffiecient])
                    senses.append("G")
                    rhs.append(instance.p[j][i] - 3 * M)

    # constarint 4
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                for k in range(instance.m[i]):
                    variables = ["C_{}_{}".format(j1, i)]
                    variables += ["C_{}_{}".format(j, i)]
                    variables += ["X_{}_{}_{}".format(j, j1, i)]
                    variables += ["Y_{}_{}_{}".format(j, i, k)]
                    variables += ["Y_{}_{}_{}".format(j1, i, k)]
                    coffiecient = [1, -1, M, -M, -M]
                    constraints.append([variables, coffiecient])
                    senses.append("G")
                    rhs.append(instance.p[j1][i] - 2 * M)

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