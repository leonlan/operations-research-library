def minimize_completion_times(data, mdl, tasks):
    completion_times = [mdl.end_of(tasks[j][-1]) for j in range(data.num_jobs)]
    mdl.add(mdl.minimize(mdl.sum(completion_times)))
