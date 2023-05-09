def add_sequence_variables(data, mdl, tasks):
    sequence_vars = [
        mdl.sequence_var([tasks[j][i] for j in range(data.jobs)])
        for i in range(data.machines)
    ]
    return sequence_vars
