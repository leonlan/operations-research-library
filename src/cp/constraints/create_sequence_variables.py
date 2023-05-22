def create_sequence_variables(data, mdl, tasks):
    sequence_vars = [
        mdl.sequence_var([tasks[j][i] for j in range(data.num_jobs)])
        for i in range(data.num_machines)
    ]
    return sequence_vars
