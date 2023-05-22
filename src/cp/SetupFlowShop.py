import docplex.cp.model as docp

from .constraints import create_task_interval_variables
from .constraints.add_sequence_variables import create_sequence_variables
from .constraints.all_machines_same_sequence import (
    same_sequence_on_each_machine,
)
from .constraints.minimize_makespan import minimize_makespan
from .constraints.no_overlap_between_machines import (
    no_overlap_between_machines,
)


def SetupFlowShop(data):
    mdl = docp.CpoModel()

    tasks = create_task_interval_variables(data, mdl)
    no_overlap_between_machines(data, mdl, tasks)

    machine_sequence = create_sequence_variables(data, mdl, tasks)
    same_sequence_on_each_machine(data, machine_sequence, mdl)

    for i in range(data.num_machines):
        mdl.add(mdl.no_overlap(machine_sequence[i], data.setup[i]))

    minimize_makespan(data, mdl, tasks)

    return mdl
