def create_sequence_variables(data, model, tasks):
    sequence_vars = [
        model.sequence_var([tasks[j][i] for j in range(data.num_jobs)])
        for i in range(data.num_machines)
    ]
    return sequence_vars
