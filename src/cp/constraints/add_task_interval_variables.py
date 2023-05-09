def add_task_interval_variables(data, mdl):
    tasks = [
        [
            mdl.interval_var(name=f"T_{j}_{i}", size=data.processing[j][i])
            for i in range(data.num_machines)
        ]
        for j in range(data.num_jobs)
    ]

    return tasks
