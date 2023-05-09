def no_overlap_machines(data, machine_sequence, mdl):
    for i in range(data.g):
        mdl.add(mdl.no_overlap(machine_sequence[i]))  # no overlap machines
