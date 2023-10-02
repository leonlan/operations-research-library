from .constants import M, V


def DistributedFlowShop(data, mdl):
    jobs = range(data.num_jobs)
    stages = range(data.num_machines)
    factories = range(data.num_factories)

    # Variable Y
    names = [f"Y_{j}_{k}" for j in jobs for k in factories]
    objective = [0] * len(names)
    lower_bounds = [0] * len(names)
    upper_bounds = [1] * len(names)
    types = ["B"] * len(names)

    # Variable X
    names += [
        f"X_{j}_{j1}" for j in jobs for j1 in range(j + 1, data.num_jobs)
    ]
    objective += [0 for j in jobs for _ in range(j + 1, data.num_jobs)]
    lower_bounds += [0 for j in jobs for _ in range(j + 1, data.num_jobs)]
    upper_bounds += [1 for j in jobs for _ in range(j + 1, data.num_jobs)]
    types += ["B" for j in jobs for _ in range(j + 1, data.num_jobs)]

    # Variable C
    names += [f"C_{j}_{i}" for j in jobs for i in stages]
    objective += [0] * data.num_jobs * data.num_machines
    lower_bounds += [0] * data.num_jobs * data.num_machines
    upper_bounds += [V] * data.num_jobs * data.num_machines
    types += ["C"] * data.num_jobs * data.num_machines

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
    for j in jobs:
        variables = [f"Y_{j}_{k}" for k in factories]
        coffiecient = [1] * data.num_factories
        constraints.append([variables, coffiecient])
        senses.append("E")
        rhs.append(1)

    # constraint 2-1
    for j in jobs:
        variables = [f"C_{j}_0"]
        coffiecient = [1]
        constraints.append([variables, coffiecient])
        senses.append("G")
        rhs.append(data.processing[j][0])

    # constraint 2-2
    for j in jobs:
        for i in range(1, data.num_machines):
            variables = [f"C_{j}_{i}"]
            variables += [f"C_{j}_{i - 1}"]
            coffiecient = [1, -1]
            constraints.append([variables, coffiecient])
            senses.append("G")
            rhs.append(data.processing[j][i])

    # constraint 3
    for j in range(data.num_jobs - 1):
        for j1 in range(j + 1, data.num_jobs):
            for i in stages:
                for k in factories:
                    variables = [f"C_{j}_{i}"]
                    variables += [f"C_{j1}_{i}"]
                    variables += [f"X_{j}_{j1}"]
                    variables += [f"Y_{j}_{k}"]
                    variables += [f"Y_{j1}_{k}"]
                    coffiecient = [1, -1, -M, -M, -M]
                    constraints.append([variables, coffiecient])
                    senses.append("G")
                    rhs.append(data.processing[j][i] - 3 * M)

    for j in range(data.num_jobs - 1):
        for j1 in range(j + 1, data.num_jobs):
            for i in stages:
                for k in factories:
                    variables = [f"C_{j1}_{i}"]
                    variables += [f"C_{j}_{i}"]
                    variables += [f"X_{j}_{j1}"]
                    variables += [f"Y_{j}_{k}"]
                    variables += [f"Y_{j1}_{k}"]
                    coffiecient = [1, -1, M, -M, -M]
                    constraints.append([variables, coffiecient])
                    senses.append("G")
                    rhs.append(data.processing[j1][i] - 2 * M)

    for j in jobs:
        variables = ["C_max"]
        variables += [f"C_{j}_{data.num_machines - 1}"]
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
