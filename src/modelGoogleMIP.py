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


def parallelmachinemodel(instance, mdl):
    Y = [
        [mdl.BoolVar(f"Y[{j}][{i}]") for i in range(instance.g)]
        for j in range(instance.n)
    ]
    C_max = mdl.NumVar(0, mdl.infinity(), "C_max")

    # constarint 1
    for j in range(instance.n):
        mdl.Add(sum([Y[j][i] for i in range(instance.g)]) == 1)

    # constarint 2
    for i in range(instance.g):
        mdl.Add(
            C_max
            - sum([instance.p[j][i] * Y[j][i] for j in range(instance.n)])
            >= 0
        )

    mdl.Minimize(C_max)

    return mdl


def Distributedflowshopmodel(instance, mdl):
    Y = [
        [mdl.BoolVar(f"Y[{j}][{k}]") for k in range(instance.f)]
        for j in range(instance.n)
    ]
    X = [
        [mdl.BoolVar(f"X[{j}][{j1}]") for j1 in range(instance.n)]
        for j in range(instance.n)
    ]
    C = [
        [
            mdl.NumVar(0, mdl.infinity(), f"C[{j}][{i}]")
            for i in range(instance.g)
        ]
        for j in range(instance.n)
    ]
    C_max = mdl.NumVar(0, mdl.infinity(), "C_max")

    # constarint 1
    for j in range(instance.n):
        mdl.Add(sum([Y[j][k] for k in range(instance.f)]) == 1)

    # constarint 2
    for j in range(instance.n):
        mdl.Add(C[j][0] >= instance.p[j][0])

    # constarint 2-1
    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.Add(C[j][i] - C[j][i - 1] >= instance.p[j][i])

    # constarint 3
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                for k in range(instance.f):
                    mdl.Add(
                        C[j][i]
                        - C[j1][i]
                        - M * Y[j][k]
                        - M * Y[j1][k]
                        - M * X[j][j1]
                        >= instance.p[j][i] - 3 * M
                    )

    # constarint 4
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                for k in range(instance.f):
                    mdl.Add(
                        C[j1][i]
                        - C[j][i]
                        - M * Y[j][k]
                        - M * Y[j1][k]
                        + M * X[j][j1]
                        >= instance.p[j1][i] - 2 * M
                    )

    # constarint 5
    for j in range(instance.n):
        mdl.Add(C_max - C[j][instance.g - 1] >= 0)

    mdl.Minimize(C_max)

    return mdl


def Nowaitflowshopmodel(instance, mdl):
    X = [
        [mdl.BoolVar(f"X[{j}][{j1}]") for j1 in range(instance.n)]
        for j in range(instance.n)
    ]
    C = [
        [
            mdl.NumVar(0, mdl.infinity(), f"C[{j}][{i}]")
            for i in range(instance.g)
        ]
        for j in range(instance.n)
    ]
    C_max = mdl.NumVar(0, mdl.infinity(), "C_max")

    # constarint 1
    for j in range(instance.n):
        mdl.Add(C[j][0] >= instance.p[j][0])

    # constarint 2
    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.Add(C[j][i] - C[j][i - 1] == instance.p[j][i])

    # constarint 3
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                mdl.Add(
                    C[j][i] - C[j1][i] - M * X[j][j1] >= instance.p[j][i] - M
                )

    # constarint 4
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                mdl.Add(C[j1][i] - C[j][i] + M * X[j][j1] >= instance.p[j1][i])

    # constarint 5
    for j in range(instance.n):
        mdl.Add(C_max - C[j][instance.g - 1] >= 0)

    mdl.Minimize(C_max)

    return mdl


def Setupflowshopmodel(instance, mdl):
    X = [
        [mdl.BoolVar(f"X[{j}][{j1}]") for j1 in range(instance.n + 1)]
        for j in range(instance.n + 1)
    ]
    C = [
        [
            mdl.NumVar(0, mdl.infinity(), f"C[{j}][{i}]")
            for i in range(instance.g)
        ]
        for j in range(instance.n + 1)
    ]
    C_max = mdl.NumVar(0, mdl.infinity(), "C_max")

    # constarint 1
    for j in range(1, instance.n + 1):
        mdl.Add(
            sum([X[j][j1] for j1 in range(instance.n + 1) if j1 != j]) == 1
        )

    # constarint 2
    for j1 in range(1, instance.n + 1):
        mdl.Add(
            sum([X[j][j1] for j in range(1, instance.n + 1) if j1 != j]) <= 1
        )

    # constarint 2-1
    mdl.Add(sum([X[j][0] for j in range(1, instance.n + 1)]) == 1)

    # constarint 3
    for j in range(1, instance.n + 1):
        for i in range(1, instance.g):
            mdl.Add(C[j][i] - C[j][i - 1] >= instance.p[j - 1][i])

    # constarint 4
    for j in range(1, instance.n + 1):
        for j1 in range(instance.n + 1):
            if j1 != j:
                for i in range(instance.g):
                    if j1 == 0:
                        mdl.Add(
                            C[j][i] - C[j1][i] - M * X[j][j1]
                            >= instance.p[j - 1][i] - M
                        )
                    else:
                        mdl.Add(
                            C[j][i] - C[j1][i] - M * X[j][j1]
                            >= instance.p[j - 1][i]
                            + instance.s[i][j1 - 1][j - 1]
                            - M
                        )

    # constarint 5
    for j in range(1, instance.n + 1):
        mdl.Add(C_max - C[j][instance.g - 1] >= 0)

    mdl.Minimize(C_max)

    return mdl


def Tardinessflowshopmodel(instance, mdl):
    X = [
        [mdl.BoolVar(f"X[{j}][{j1}]") for j1 in range(instance.n)]
        for j in range(instance.n)
    ]
    C = [
        [
            mdl.NumVar(0, mdl.infinity(), f"C[{j}][{i}]")
            for i in range(instance.g)
        ]
        for j in range(instance.n)
    ]
    T = [mdl.NumVar(0, mdl.infinity(), f"T[{j}]") for j in range(instance.n)]

    # constarint 1
    for j in range(instance.n):
        mdl.Add(C[j][0] >= instance.p[j][0])

    # constarint 2
    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.Add(C[j][i] - C[j][i - 1] >= instance.p[j][i])

    # constarint 3
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                mdl.Add(
                    C[j][i] - C[j1][i] - M * X[j][j1] >= instance.p[j][i] - M
                )

    # constarint 4
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                mdl.Add(C[j1][i] - C[j][i] + M * X[j][j1] >= instance.p[j1][i])

    # constarint 5
    for j in range(instance.n):
        mdl.Add(T[j] - C[j][instance.g - 1] >= -1 * instance.d[j])

    mdl.Minimize(sum([T[j] for j in range(instance.n)]))

    return mdl


def TCTflowshopmodel(instance, mdl):
    X = [
        [mdl.BoolVar(f"X[{j}][{j1}]") for j1 in range(instance.n)]
        for j in range(instance.n)
    ]
    C = [
        [
            mdl.NumVar(0, mdl.infinity(), f"C[{j}][{i}]")
            for i in range(instance.g)
        ]
        for j in range(instance.n)
    ]

    # constarint 1
    for j in range(instance.n):
        mdl.Add(C[j][0] >= instance.p[j][0])

    # constarint 2
    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.Add(C[j][i] - C[j][i - 1] >= instance.p[j][i])

    # constarint 3
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                mdl.Add(
                    C[j][i] - C[j1][i] - M * X[j][j1] >= instance.p[j][i] - M
                )

    # constarint 4
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                mdl.Add(C[j1][i] - C[j][i] + M * X[j][j1] >= instance.p[j1][i])

    mdl.Minimize(sum([C[j][instance.g - 1] for j in range(instance.n)]))

    return mdl


def flowshopmodel(instance, mdl):
    X = [
        [mdl.BoolVar(f"X[{j}][{j1}]") for j1 in range(instance.n)]
        for j in range(instance.n)
    ]
    C = [
        [
            mdl.NumVar(0, mdl.infinity(), f"C[{j}][{i}]")
            for i in range(instance.g)
        ]
        for j in range(instance.n)
    ]
    C_max = mdl.NumVar(0, mdl.infinity(), "C_max")

    # constarint 1
    for j in range(instance.n):
        mdl.Add(C[j][0] >= instance.p[j][0])

    # constarint 2
    for j in range(instance.n):
        for i in range(1, instance.g):
            mdl.Add(C[j][i] - C[j][i - 1] >= instance.p[j][i])

    # constarint 3
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                mdl.Add(
                    C[j][i] - C[j1][i] - M * X[j][j1] >= instance.p[j][i] - M
                )

    # constarint 4
    for j in range(instance.n - 1):
        for j1 in range(j + 1, instance.n):
            for i in range(instance.g):
                mdl.Add(C[j1][i] - C[j][i] + M * X[j][j1] >= instance.p[j1][i])

    # constarint 5
    for j in range(instance.n):
        mdl.Add(C_max - C[j][instance.g - 1] >= 0)

    mdl.Minimize(C_max)

    return mdl
