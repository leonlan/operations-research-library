def add_sequence_variables(data, mdl, tasks):
    sequence_vars = [
        mdl.sequence_var([tasks[j][i] for j in range(data.n)])
        for i in range(data.g)
    ]
    return sequence_vars
