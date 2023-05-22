import docplex.cp.model as docp

from .constraints import create_task_interval_variables
from .constraints.add_sequence_variables import create_sequence_variables
from .constraints.all_machines_same_sequence import (
    same_sequence_on_each_machine,
)
from .constraints.no_overlap_between_machines import (
    no_overlap_between_machines,
)
from .constraints.no_overlap_on_machines import no_overlap_on_machines


def base_model(data):
    """
    Creates a base model and variables for the permutation flow shop problem.
    This can be extended with different constraints and objective functions.
    """
    mdl = docp.CpoModel()

    tasks = create_task_interval_variables(data, mdl)
    no_overlap_between_machines(data, mdl, tasks)

    sequences = create_sequence_variables(data, mdl, tasks)
    no_overlap_on_machines(data, sequences, mdl)
    same_sequence_on_each_machine(data, sequences, mdl)

    return mdl, tasks, sequences
