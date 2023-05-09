from .constants import M, V


def Nowaitflowshopmodel(data, mdl):
    # Variable X
    names = [
        "X_{}_{}".format(j, j1)
        for j in range(data.jobs)
        for j1 in range(j + 1, data.jobs)
    ]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)
    # Variable C
    names += [
        "C_{}_{}".format(j, i)
        for j in range(data.jobs)
        for i in range(data.machines)
    ]
    objective += [0] * data.jobs * data.machines
    lower_bounds += [0] * data.jobs * data.machines
    upper_bounds += [V] * data.jobs * data.machines
    types += ["C"] * data.jobs * data.machines

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
    for j in range(data.jobs):
        variables = ["C_{}_{}".format(j, 0)]
        coffiecient = [1]
        constraints.append([variables, coffiecient])
        senses.append("G")
        rhs.append(data.processing[j][0])

    # constraint 2
    for j in range(data.jobs):
        for i in range(1, data.machines):
            variables = ["C_{}_{}".format(j, i)]
            variables += ["C_{}_{}".format(j, i - 1)]
            coffiecient = [1, -1]
            constraints.append([variables, coffiecient])
            senses.append("E")
            rhs.append(data.processing[j][i])

    # constraint 3
    for j in range(data.jobs - 1):
        for j1 in range(j + 1, data.jobs):
            for i in range(data.machines):
                variables = ["C_{}_{}".format(j, i)]
                variables += ["C_{}_{}".format(j1, i)]
                variables += ["X_{}_{}".format(j, j1)]
                coffiecient = [1, -1, -M]
                constraints.append([variables, coffiecient])
                senses.append("G")
                rhs.append(data.processing[j][i] - M)

    # constraint 4
    for j in range(data.jobs - 1):
        for j1 in range(j + 1, data.jobs):
            for i in range(data.machines):
                variables = ["C_{}_{}".format(j1, i)]
                variables += ["C_{}_{}".format(j, i)]
                variables += ["X_{}_{}".format(j, j1)]
                coffiecient = [1, -1, M]
                constraints.append([variables, coffiecient])
                senses.append("G")
                rhs.append(data.processing[j1][i])

    # constraint 5
    for j in range(data.jobs):
        variables = ["C_max"]
        variables += ["C_{}_{}".format(j, data.machines - 1)]
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
