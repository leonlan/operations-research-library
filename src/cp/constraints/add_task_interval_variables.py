def add_task_interval_variables(data, mdl):
    tasks = [
        [
            mdl.interval_var(name=f"T_{j}_{i}", size=data.processing[j][i])
            for i in range(data.machines)
        ]
        for j in range(data.jobs)
    ]

    return tasks
