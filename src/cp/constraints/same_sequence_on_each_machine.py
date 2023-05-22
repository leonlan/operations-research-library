def same_sequence_on_each_machine(data, machine_sequence, model):
    for i in range(data.num_machines - 1):
        model.add(
            model.same_sequence(machine_sequence[i], machine_sequence[i + 1])
        )
