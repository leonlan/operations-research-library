def no_overlap_jobs(data, mdl, tasks):
    for j in range(data.n):
        for i in range(1, data.g):
            mdl.add(mdl.end_before_start(tasks[j][i - 1], tasks[j][i]))
