from .constants import M, V


def Setupflowshopmodel(instance, mdl):
    # Variable X
    names = [
        "X_{}_{}".format(j, j1)
        for j in range(1, instance.n + 1)
        for j1 in range(instance.n + 1)
    ]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)
    # Variable C
    names += [
        "C_{}_{}".format(j, i)
        for j in range(instance.n + 1)
        for i in range(instance.g)
    ]
    objective += [0] * (instance.n + 1) * instance.g
    lower_bounds += [0] * (instance.n + 1) * instance.g
    upper_bounds += [V] * (instance.n + 1) * instance.g
    types += ["C"] * (instance.n + 1) * instance.g

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
    for j in range(1, instance.n + 1):
        variables = [
            "X_{}_{}".format(j, j1) for j1 in range(instance.n + 1) if j1 != j
        ]
        coffiecient = [1 for j1 in range(instance.n + 1) if j1 != j]
        constraints.append([variables, coffiecient])
        senses.append("E")
        rhs.append(1)

    # constarint 2
    for j1 in range(1, instance.n + 1):
        variables = [
            "X_{}_{}".format(j, j1)
            for j in range(1, instance.n + 1)
            if j1 != j
        ]
        coffiecient = [1 for j in range(1, instance.n + 1) if j1 != j]
        constraints.append([variables, coffiecient])
        senses.append("L")
        rhs.append(1)

    # constarint 2-1
    variables = ["X_{}_{}".format(j, 0) for j in range(1, instance.n + 1)]
    coffiecient = [1 for j in range(1, instance.n + 1)]
    constraints.append([variables, coffiecient])
    senses.append("E")
    rhs.append(1)

    # constarint 3
    for j in range(1, instance.n + 1):
        for i in range(1, instance.g):
            variables = ["C_{}_{}".format(j, i)]
            variables += ["C_{}_{}".format(j, i - 1)]
            coffiecient = [1, -1]
            constraints.append([variables, coffiecient])
            senses.append("G")
            rhs.append(instance.p[j - 1][i])

    # constarint 4
    for j in range(1, instance.n + 1):
        for j1 in range(instance.n + 1):
            if j1 != j:
                for i in range(instance.g):
                    variables = ["C_{}_{}".format(j, i)]
                    variables += ["C_{}_{}".format(j1, i)]
                    variables += ["X_{}_{}".format(j, j1)]
                    coffiecient = [1, -1, -M]
                    constraints.append([variables, coffiecient])
                    senses.append("G")
                    if j1 == 0:
                        rhs.append(instance.p[j - 1][i] - M)
                    else:
                        rhs.append(
                            instance.p[j - 1][i]
                            + instance.s[i][j1 - 1][j - 1]
                            - M
                        )

    # constarint 5
    for j in range(1, instance.n + 1):
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
