def Flexiblejobshopmodel(instance, mdl):
    # Variable Z
    names = [
        "Z_{}_{}_{}".format(j, k, i)
        for j in range(instance.n)
        for k in range(instance.o[j])
        for i in range(instance.g)
    ]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)
    # Variable X
    names += [
        "X_{}_{}_{}_{}".format(j, k, j1, k1)
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
        for k in range(instance.o[j])
        for k1 in range(instance.o[j1])
    ]
    objective += [
        0
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
        for k in range(instance.o[j])
        for k1 in range(instance.o[j1])
    ]
    lower_bounds += [
        0
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
        for k in range(instance.o[j])
        for k1 in range(instance.o[j1])
    ]
    upper_bounds += [
        1
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
        for k in range(instance.o[j])
        for k1 in range(instance.o[j1])
    ]
    types += [
        "B"
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
        for k in range(instance.o[j])
        for k1 in range(instance.o[j1])
    ]
    # Variable C
    names += [
        "C_{}_{}".format(j, k)
        for j in range(instance.n)
        for k in range(instance.o[j])
    ]
    objective += [0 for j in range(instance.n) for k in range(instance.o[j])]
    lower_bounds += [
        0 for j in range(instance.n) for k in range(instance.o[j])
    ]
    upper_bounds += [
        V for j in range(instance.n) for k in range(instance.o[j])
    ]
    types += ["C" for j in range(instance.n) for k in range(instance.o[j])]

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
        for k in range(instance.o[j]):
            variables = [
                "Z_{}_{}_{}".format(j, k, i)
                for i in range(instance.g)
                if instance.p[j][k][i] > 0
            ]
            coffiecient = [
                1 for i in range(instance.g) if instance.p[j][k][i] > 0
            ]
            constraints.append([variables, coffiecient])
            senses.append("E")
            rhs.append(1)

    # constarint 2
    for j in range(instance.n):
        for k in range(instance.o[j]):
            variables = ["C_{}_{}".format(j, k)]
            coffiecient = [1]
            if k > 0:
                variables += ["C_{}_{}".format(j, k - 1)]
                coffiecient += [-1]
            variables += [
                "Z_{}_{}_{}".format(j, k, i)
                for i in range(instance.g)
                if instance.p[j][k][i] > 0
            ]
            coffiecient += [
                -instance.p[j][k][i]
                for i in range(instance.g)
                if instance.p[j][k][i] > 0
            ]
            constraints.append([variables, coffiecient])
            senses.append("G")
            rhs.append(0)

    # constarint 3
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for k in range(instance.o[j]):
                for k1 in range(instance.o[j1]):
                    for i in range(instance.g):
                        if (
                            instance.p[j][k][i] > 0
                            and instance.p[j1][k1][i] > 0
                        ):
                            variables = ["C_{}_{}".format(j, k)]
                            variables += ["C_{}_{}".format(j1, k1)]
                            variables += ["X_{}_{}_{}_{}".format(j, k, j1, k1)]
                            variables += ["Z_{}_{}_{}".format(j, k, i)]
                            variables += ["Z_{}_{}_{}".format(j1, k1, i)]
                            coffiecient = [1, -1, -M, -M, -M]
                            constraints.append([variables, coffiecient])
                            senses.append("G")
                            rhs.append(instance.p[j][k][i] - 3 * M)

    # constarint 4
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for k in range(instance.o[j]):
                for k1 in range(instance.o[j1]):
                    for i in range(instance.g):
                        if (
                            instance.p[j][k][i] > 0
                            and instance.p[j1][k1][i] > 0
                        ):
                            variables = ["C_{}_{}".format(j1, k1)]
                            variables += ["C_{}_{}".format(j, k)]
                            variables += ["X_{}_{}_{}_{}".format(j, k, j1, k1)]
                            variables += ["Z_{}_{}_{}".format(j, k, i)]
                            variables += ["Z_{}_{}_{}".format(j1, k1, i)]
                            coffiecient = [1, -1, M, -M, -M]
                            constraints.append([variables, coffiecient])
                            senses.append("G")
                            rhs.append(instance.p[j1][k1][i] - 2 * M)

    # constarint 5
    for j in range(instance.n):
        variables = ["C_max"]
        variables += ["C_{}_{}".format(j, instance.o[j] - 1)]
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
