def minimize_makespan(data, model, tasks):
    makespan = model.max(
        [model.end_of(tasks[j][data.num_machines - 1]) for j in data.jobs]
    )
    model.add(model.minimize(makespan))
