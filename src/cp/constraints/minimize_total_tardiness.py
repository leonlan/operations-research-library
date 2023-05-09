def minimize_total_tardiness(data, mdl, tasks):
    tardiness = []

    for j in range(data.num_jobs):
        lateness = mdl.end_of(tasks[j][-1]) - data.due_dates[j]
        tardiness.append(mdl.max([lateness, 0]))

    mdl.add(mdl.minimize(mdl.sum(tardiness)))
