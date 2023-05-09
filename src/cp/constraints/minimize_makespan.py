def minimize_makespan(data, mdl, tasks):
    makespan = mdl.max(
        [mdl.end_of(tasks[j][data.machines - 1]) for j in range(data.jobs)]
    )
    mdl.add(mdl.minimize(makespan))
