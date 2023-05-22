import docplex.cp.model as docp

from .constraints import create_task_interval_variables
from .constraints.create_sequence_variables import create_sequence_variables
from .constraints.minimize_makespan import minimize_makespan
from .constraints.no_overlap_between_machines import (
    no_overlap_between_machines,
)
from .constraints.same_sequence_on_each_machine import (
    same_sequence_on_each_machine,
)


def SetupFlowShop(data):
    model = docp.CpoModel()

    tasks = create_task_interval_variables(data, model)
    no_overlap_between_machines(data, model, tasks)

    machine_sequence = create_sequence_variables(data, model, tasks)
    same_sequence_on_each_machine(data, machine_sequence, model)

    for i in range(data.num_machines):
        model.add(model.no_overlap(machine_sequence[i], data.setup[i]))

    minimize_makespan(data, model, tasks)

    return model
