from .constants import V


def parallelmachinemodel(data, mdl):
    # Variable Y
    names = [
        "Y_{}_{}".format(j, i)
        for j in range(data.jobs)
        for i in range(data.machines)
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

    # constraint 1
    for j in range(data.jobs):
        variables = ["Y_{}_{}".format(j, i) for i in range(data.machines)]
        coffiecient = [1] * data.machines
        constraints.append([variables, coffiecient])
        senses.append("E")
        rhs.append(1)

    # constraint 2
    for i in range(data.machines):
        variables = ["C_max"]
        coffiecient = [1]
        variables += ["Y_{}_{}".format(j, i) for j in range(data.jobs)]
        coffiecient += [-1 * data.processing[j][i] for j in range(data.jobs)]
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
