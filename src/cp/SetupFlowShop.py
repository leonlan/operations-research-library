import docplex.cp.model as docp

from .constraints import (
    create_sequence_variables,
    create_task_interval_variables,
    minimize_makespan,
    no_overlap_between_machines,
    same_sequence_on_each_machine,
)


def SetupFlowShop(data):
    model = docp.CpoModel()

    tasks = create_task_interval_variables(data, model)
    no_overlap_between_machines(data, model, tasks)

    machine_sequence = create_sequence_variables(data, model, tasks)
    same_sequence_on_each_machine(data, machine_sequence, model)

    for i in data.machines:
        model.add(model.no_overlap(machine_sequence[i], data.setup[i]))

    minimize_makespan(data, model, tasks)

    return model
