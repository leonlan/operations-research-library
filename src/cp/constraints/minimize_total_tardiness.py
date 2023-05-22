def minimize_total_tardiness(data, model, tasks):
    tardiness = []

    for j in range(data.num_jobs):
        lateness = model.end_of(tasks[j][-1]) - data.due_dates[j]
        tardiness.append(model.max([lateness, 0]))

    model.add(model.minimize(model.sum(tardiness)))
