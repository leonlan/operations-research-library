from .constants import M, V


def SetupFlowShop(data, mdl):
    # Variable X
    names = [
        "X_{}_{}".format(j, j1)
        for j in range(1, data.num_jobs + 1)
        for j1 in range(data.num_jobs + 1)
    ]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)
    # Variable C
    names += [
        "C_{}_{}".format(j, i)
        for j in range(data.num_jobs + 1)
        for i in range(data.num_machines)
    ]
    objective += [0] * (data.num_jobs + 1) * data.num_machines
    lower_bounds += [0] * (data.num_jobs + 1) * data.num_machines
    upper_bounds += [V] * (data.num_jobs + 1) * data.num_machines
    types += ["C"] * (data.num_jobs + 1) * data.num_machines

    # Variable Cmax
    names += ["C_max"]
    objective += [1]
    lower_bounds += [0]
    upper_bounds += [V]
    types += ["C"]

    ###### constraints ########
    constraints = []
    senses = []
    rhs = []

    # constraint 1
    for j in range(1, data.num_jobs + 1):
        variables = [
            "X_{}_{}".format(j, j1)
            for j1 in range(data.num_jobs + 1)
            if j1 != j
        ]
        coffiecient = [1 for j1 in range(data.num_jobs + 1) if j1 != j]
        constraints.append([variables, coffiecient])
        senses.append("E")
        rhs.append(1)

    # constraint 2
    for j1 in range(1, data.num_jobs + 1):
        variables = [
            "X_{}_{}".format(j, j1)
            for j in range(1, data.num_jobs + 1)
            if j1 != j
        ]
        coffiecient = [1 for j in range(1, data.num_jobs + 1) if j1 != j]
        constraints.append([variables, coffiecient])
        senses.append("L")
        rhs.append(1)

    # constraint 2-1
    variables = ["X_{}_{}".format(j, 0) for j in range(1, data.num_jobs + 1)]
    coffiecient = [1 for j in range(1, data.num_jobs + 1)]
    constraints.append([variables, coffiecient])
    senses.append("E")
    rhs.append(1)

    # constraint 3
    for j in range(1, data.num_jobs + 1):
        for i in range(1, data.num_machines):
            variables = ["C_{}_{}".format(j, i)]
            variables += ["C_{}_{}".format(j, i - 1)]
            coffiecient = [1, -1]
            constraints.append([variables, coffiecient])
            senses.append("G")
            rhs.append(data.processing[j - 1][i])

    # constraint 4
    for j in range(1, data.num_jobs + 1):
        for j1 in range(data.num_jobs + 1):
            if j1 != j:
                for i in range(data.num_machines):
                    variables = ["C_{}_{}".format(j, i)]
                    variables += ["C_{}_{}".format(j1, i)]
                    variables += ["X_{}_{}".format(j, j1)]
                    coffiecient = [1, -1, -M]
                    constraints.append([variables, coffiecient])
                    senses.append("G")
                    if j1 == 0:
                        rhs.append(data.processing[j - 1][i] - M)
                    else:
                        rhs.append(
                            data.processing[j - 1][i]
                            + data.setup[i][j1 - 1][j - 1]
                            - M
                        )

    # constraint 5
    for j in range(1, data.num_jobs + 1):
        variables = ["C_max"]
        variables += ["C_{}_{}".format(j, data.num_machines - 1)]
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
