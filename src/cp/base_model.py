import docplex.cp.model as docp

from .constraints import add_task_interval_variables
from .constraints.add_sequence_variables import add_sequence_variables
from .constraints.all_machines_same_sequence import all_machines_same_sequence
from .constraints.no_overlap_jobs import no_overlap_jobs
from .constraints.no_overlap_machines import no_overlap_machines


def base_model(data):
    mdl = docp.CpoModel()

    tasks = add_task_interval_variables(data, mdl)
    no_overlap_jobs(data, mdl, tasks)

    machine_sequence = add_sequence_variables(data, mdl, tasks)
    no_overlap_machines(data, machine_sequence, mdl)
    all_machines_same_sequence(data, machine_sequence, mdl)

    return mdl, tasks, machine_sequence
