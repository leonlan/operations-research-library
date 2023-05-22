import docplex.cp.model as docp

from .constraints import create_task_interval_variables
from .constraints.create_sequence_variables import create_sequence_variables
from .constraints.minimize_makespan import minimize_makespan
from .constraints.minimize_total_completion_times import (
    minimize_total_completion_times,
)
from .constraints.minimize_total_tardiness import minimize_total_tardiness
from .constraints.no_overlap_between_machines import (
    no_overlap_between_machines,
)
from .constraints.no_overlap_on_machines import no_overlap_on_machines
from .constraints.same_sequence_on_each_machine import (
    same_sequence_on_each_machine,
)


def FlowShop(data, objective="makespan"):
    model = docp.CpoModel()

    # Variables
    tasks = create_task_interval_variables(data, model)
    no_overlap_between_machines(data, model, tasks)

    # Constraints
    sequences = create_sequence_variables(data, model, tasks)
    no_overlap_on_machines(data, sequences, model)
    same_sequence_on_each_machine(data, sequences, model)

    # Objective
    add_objective(data, model, objective, tasks)

    return model


def add_objective(data, model, objective, tasks):
    if objective == "makespan":
        minimize_makespan(data, model, tasks)
    elif objective == "total_tardiness":
        minimize_total_tardiness(data, model, tasks)
    elif objective == "total_completion_times":
        minimize_total_completion_times(data, model, tasks)
    else:
        raise ValueError("Invalid objective function")
