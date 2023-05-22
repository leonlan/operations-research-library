def no_overlap_between_machines(data, model, tasks):
    for j in data.jobs:
        for i in range(1, data.num_machines):
            model.add(model.end_before_start(tasks[j][i - 1], tasks[j][i]))
