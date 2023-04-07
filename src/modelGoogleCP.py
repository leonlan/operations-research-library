import collections

# https://developers.google.com/optimization/reference/python/sat/python/cp_model#bestobjectivebound
# https://developers.google.com/optimization/reference/python/linear_solver/pywraplp#bestbound


###### main ########
def CPmodel_generation(instance, mdl, problemType):
    if problemType == "Flowshop":
        pass
        mdl = flowshopmodel(instance, mdl)
    if problemType == "Distributedflowshop":
        pass
        mdl = Distributedflowshopmodel(instance, mdl)
    if problemType == "Nowaitflowshop":
        mdl = Nowaitflowshopmodel(instance, mdl)  # done
    if problemType == "Setupflowshop":
        pass
        mdl = Setupflowshopmodel(instance, mdl)
    if problemType == "Tardinessflowshop":
        pass
        mdl = Tardinessflowshopmodel(instance, mdl)
    if problemType == "TCTflowshop":
        pass
        mdl = TCTflowshopmodel(instance, mdl)
    if problemType == "Parallelmachine":  # done
        mdl = prallelmachinemodel(instance, mdl)
    return mdl


def prallelmachinemodel(instance, mdl):
    Y = [
        [mdl.NewBoolVar(f"Y[{j}][{i}]") for i in range(instance.g)]
        for j in range(instance.n)
    ]
    C_max = mdl.NewIntVar(
        0, sum([max(instance.p[j]) for j in range(instance.n)]), "C_max"
    )

    for j in range(instance.n):
        mdl.AddExactlyOne(Y[j][i] for i in range(instance.g))
    mdl.AddMaxEquality(
        C_max,
        [
            sum([instance.p[j][i] * Y[j][i] for j in range(instance.n)])
            for i in range(instance.g)
        ],
    )
    mdl.Minimize(C_max)

    return mdl


def Nowaitflowshopmodel(instance, mdl):
    horizon = sum([sum(instance.p[j]) for j in range(instance.n)])

    task_type = collections.namedtuple("task_type", "start end interval")
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)

    for j in range(instance.n):
        for i in range(instance.g):
            suffix = "_%i_%i" % (j, i)
            start_var = mdl.NewIntVar(0, horizon, "start" + suffix)
            end_var = mdl.NewIntVar(0, horizon, "end" + suffix)
            interval_var = mdl.NewIntervalVar(
                start_var, instance.p[j][i], end_var, "interval" + suffix
            )
            all_tasks[j, i] = task_type(
                start=start_var, end=end_var, interval=interval_var
            )
            machine_to_intervals[i].append(interval_var)

    for i in range(instance.g):
        mdl.AddNoOverlap(machine_to_intervals[i])

    for j in range(instance.n):
        for i in range(instance.g - 1):
            mdl.Add(all_tasks[j, i + 1].start == all_tasks[j, i].end)

    C_max = mdl.NewIntVar(0, horizon, "C_max")
    mdl.AddMaxEquality(
        C_max, [all_tasks[j, instance.g - 1].end for j in range(instance.n)]
    )
    mdl.Minimize(C_max)

    return mdl
