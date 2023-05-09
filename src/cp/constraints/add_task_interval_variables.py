def add_task_interval_variables(data, mdl):
    tasks = [
        [
            mdl.interval_var(name=f"T_{j}_{i}", size=data.p[j][i])
            for i in range(data.g)
        ]
        for j in range(data.n)
    ]

    return tasks
