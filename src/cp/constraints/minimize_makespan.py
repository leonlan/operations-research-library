def minimize_makespan(data, mdl, tasks):
    makespan = mdl.max(
        [
            mdl.end_of(tasks[j][data.num_machines - 1])
            for j in range(data.num_jobs)
        ]
    )
    mdl.add(mdl.minimize(makespan))
