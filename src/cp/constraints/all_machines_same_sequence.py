def all_machines_same_sequence(data, machine_sequence, mdl):
    for i in range(data.machines - 1):
        mdl.add(
            mdl.same_sequence(machine_sequence[i], machine_sequence[i + 1])
        )
