def no_overlap_on_machines(data, model, sequence, include_setup=False):
    """
    Adds the no overlap constraint on machines to the model.

    Parameters
    ----------
    data
        An object containing the problem data.
    model
        The model to which the constraint is added.
    sequence
        The sequence of interval vars for each machine.
    include_setup
        Whether to use the setup times or not. The default is False. If set,
        then the problem data must have a ``setup`` field.
    """
    for i in data.machines:
        if include_setup:
            model.add(model.no_overlap(sequence[i], data.setup[i]))
        else:
            model.add(model.no_overlap(sequence[i]))
