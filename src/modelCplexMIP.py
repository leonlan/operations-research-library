M = 100000  # Big M
V = 10000000  # upper bound for variables


###### main ########
def MIPmodel_generation(instance, mdl, problemType):
    if problemType == "Flowshop":
        mdl = flowshopmodel(instance, mdl)
    if problemType == "Distributedflowshop":
        mdl = Distributedflowshopmodel(instance, mdl)
    if problemType == "Nowaitflowshop":
        mdl = Nowaitflowshopmodel(instance, mdl)
    if problemType == "Setupflowshop":
        mdl = Setupflowshopmodel(instance, mdl)
    if problemType == "Tardinessflowshop":
        mdl = Tardinessflowshopmodel(instance, mdl)
    if problemType == "TCTflowshop":
        mdl = TCTflowshopmodel(instance, mdl)
    if problemType == "Parallelmachine":
        mdl = parallelmachinemodel(instance, mdl)
    return mdl


def TCTflowshopmodel(instance, mdl):
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
    for _j in range(instance.n):
        for _i in range(instance.g - 1):
            objective += [0]
        objective += [1]
    lower_bounds += [0] * instance.n * instance.g
    upper_bounds += [V] * instance.n * instance.g
    types += ["C"] * instance.n * instance.g

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


def Tardinessflowshopmodel(instance, mdl):
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

    # Variable T
    names += ["T_{}".format(j) for j in range(instance.n)]
    objective += [1] * instance.n
    lower_bounds += [0] * instance.n
    upper_bounds += [V] * instance.n
    types += ["C"] * instance.n

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
        variables = ["T_{}".format(j)]
        variables += ["C_{}_{}".format(j, instance.g - 1)]
        coffiecient = [1, -1]
        constraints.append([variables, coffiecient])
        senses.append("G")
        rhs.append(-1 * instance.d[j])

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


def Nowaitflowshopmodel(instance, mdl):
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
            senses.append("E")
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


def Distributedflowshopmodel(instance, mdl):
    # Variable Y
    names = [
        "Y_{}_{}".format(j, k)
        for j in range(instance.n)
        for k in range(instance.f)
    ]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)

    # Variable X
    names += [
        "X_{}_{}".format(j, j1)
        for j in range(instance.n)
        for j1 in range(j + 1, instance.n)
    ]
    objective += [
        0 for j in range(instance.n) for j1 in range(j + 1, instance.n)
    ]
    lower_bounds += [
        0 for j in range(instance.n) for j1 in range(j + 1, instance.n)
    ]
    upper_bounds += [
        1 for j in range(instance.n) for j1 in range(j + 1, instance.n)
    ]
    types += [
        "B" for j in range(instance.n) for j1 in range(j + 1, instance.n)
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
        variables = ["Y_{}_{}".format(j, k) for k in range(instance.f)]
        coffiecient = [1] * instance.f
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
                for k in range(instance.f):
                    variables = ["C_{}_{}".format(j, i)]
                    variables += ["C_{}_{}".format(j1, i)]
                    variables += ["X_{}_{}".format(j, j1)]
                    variables += ["Y_{}_{}".format(j, k)]
                    variables += ["Y_{}_{}".format(j1, k)]
                    coffiecient = [1, -1, -M, -M, -M]
                    constraints.append([variables, coffiecient])
                    senses.append("G")
                    rhs.append(instance.p[j][i] - 3 * M)

    # constarint 4
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                for k in range(instance.f):
                    variables = ["C_{}_{}".format(j1, i)]
                    variables += ["C_{}_{}".format(j, i)]
                    variables += ["X_{}_{}".format(j, j1)]
                    variables += ["Y_{}_{}".format(j, k)]
                    variables += ["Y_{}_{}".format(j1, k)]
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
