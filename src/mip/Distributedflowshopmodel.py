from .constants import M, V


def Distributedflowshopmodel(data, mdl):
    # Variable Y
    names = [
        "Y_{}_{}".format(j, k) for j in range(data.n) for k in range(data.f)
    ]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)

    # Variable X
    names += [
        "X_{}_{}".format(j, j1)
        for j in range(data.n)
        for j1 in range(j + 1, data.n)
    ]
    objective += [0 for j in range(data.n) for _ in range(j + 1, data.n)]
    lower_bounds += [0 for j in range(data.n) for _ in range(j + 1, data.n)]
    upper_bounds += [1 for j in range(data.n) for _ in range(j + 1, data.n)]
    types += ["B" for j in range(data.n) for _ in range(j + 1, data.n)]

    # Variable C
    names += [
        "C_{}_{}".format(j, i) for j in range(data.n) for i in range(data.g)
    ]
    objective += [0] * data.n * data.g
    lower_bounds += [0] * data.n * data.g
    upper_bounds += [V] * data.n * data.g
    types += ["C"] * data.n * data.g

    # Variable Cmax
    names += ["C_max"]
    objective += [1]
    lower_bounds += [0]
    upper_bounds += [V]
    types += ["C"]

    constraints = []
    senses = []
    rhs = []

    # constraint 1
    for j in range(data.n):
        variables = ["Y_{}_{}".format(j, k) for k in range(data.f)]
        coffiecient = [1] * data.f
        constraints.append([variables, coffiecient])
        senses.append("E")
        rhs.append(1)

    # constraint 2-1
    for j in range(data.n):
        variables = ["C_{}_{}".format(j, 0)]
        coffiecient = [1]
        constraints.append([variables, coffiecient])
        senses.append("G")
        rhs.append(data.p[j][0])

    # constraint 2-2
    for j in range(data.n):
        for i in range(1, data.g):
            variables = ["C_{}_{}".format(j, i)]
            variables += ["C_{}_{}".format(j, i - 1)]
            coffiecient = [1, -1]
            constraints.append([variables, coffiecient])
            senses.append("G")
            rhs.append(data.p[j][i])

    # constraint 3
    for j in range(data.n - 1):
        for j1 in range(j + 1, data.n):
            for i in range(data.g):
                for k in range(data.f):
                    variables = ["C_{}_{}".format(j, i)]
                    variables += ["C_{}_{}".format(j1, i)]
                    variables += ["X_{}_{}".format(j, j1)]
                    variables += ["Y_{}_{}".format(j, k)]
                    variables += ["Y_{}_{}".format(j1, k)]
                    coffiecient = [1, -1, -M, -M, -M]
                    constraints.append([variables, coffiecient])
                    senses.append("G")
                    rhs.append(data.p[j][i] - 3 * M)

    # constraint 4
    for j in range(data.n - 1):
        for j1 in range(j + 1, data.n):
            for i in range(data.g):
                for k in range(data.f):
                    variables = ["C_{}_{}".format(j1, i)]
                    variables += ["C_{}_{}".format(j, i)]
                    variables += ["X_{}_{}".format(j, j1)]
                    variables += ["Y_{}_{}".format(j, k)]
                    variables += ["Y_{}_{}".format(j1, k)]
                    coffiecient = [1, -1, M, -M, -M]
                    constraints.append([variables, coffiecient])
                    senses.append("G")
                    rhs.append(data.p[j1][i] - 2 * M)

    for j in range(data.n):
        variables = ["C_max"]
        variables += ["C_{}_{}".format(j, data.g - 1)]
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
