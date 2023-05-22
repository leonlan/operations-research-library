def minimize_completion_times(data, model, tasks):
    completion_times = [
        model.end_of(tasks[j][-1]) for j in range(data.num_jobs)
    ]
    model.add(model.minimize(model.sum(completion_times)))
