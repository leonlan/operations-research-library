import docplex.cp.model as docp

from .constraints import create_task_interval_variables
from .constraints.create_sequence_variables import create_sequence_variables
from .constraints.no_overlap_between_machines import (
    no_overlap_between_machines,
)
from .constraints.no_overlap_on_machines import no_overlap_on_machines
from .constraints.same_sequence_on_each_machine import (
    same_sequence_on_each_machine,
)


def base_model(data):
    """
    Creates a base model and variables for the permutation flow shop problem.
    This can be extended with different constraints and objective functions.
    """
    model = docp.CpoModel()

    tasks = create_task_interval_variables(data, model)
    no_overlap_between_machines(data, model, tasks)

    sequences = create_sequence_variables(data, model, tasks)
    no_overlap_on_machines(data, sequences, model)
    same_sequence_on_each_machine(data, sequences, model)

    return model, tasks, sequences
