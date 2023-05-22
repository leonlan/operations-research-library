def create_task_interval_variables(data, model, include_processing=True):
    if include_processing:
        return [
            [
                model.interval_var(
                    name=f"T_{j}_{i}", size=data.processing[j][i]
                )
                for i in range(data.num_machines)
            ]
            for j in range(data.num_jobs)
        ]
    else:
        return [
            [
                model.interval_var(name=f"T_{j}_{i}")
                for i in range(data.num_machines)
            ]
            for j in range(data.num_jobs)
        ]
