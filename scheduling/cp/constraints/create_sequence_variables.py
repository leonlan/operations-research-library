def create_sequence_variables(data, model, tasks):
    sequence_vars = [
        model.sequence_var([tasks[j][i] for j in data.jobs])
        for i in data.machines
    ]
    return sequence_vars
