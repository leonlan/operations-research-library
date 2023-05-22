def no_overlap_on_machines(data, machine_sequence, model):
    for i in range(data.num_machines):
        model.add(model.no_overlap(machine_sequence[i]))  # no overlap machines
