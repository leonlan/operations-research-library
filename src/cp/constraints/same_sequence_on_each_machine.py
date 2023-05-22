def same_sequence_on_each_machine(data, machine_sequence, mdl):
    for i in range(data.num_machines - 1):
        mdl.add(
            mdl.same_sequence(machine_sequence[i], machine_sequence[i + 1])
        )
