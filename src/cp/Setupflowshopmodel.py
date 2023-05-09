from .constraints import add_task_interval_variables
from .constraints.add_sequence_variables import add_sequence_variables
from .constraints.all_machines_same_sequence import all_machines_same_sequence
from .constraints.minimize_makespan import minimize_makespan
from .constraints.no_overlap_jobs import no_overlap_jobs


def Setupflowshopmodel(data, mdl):
    tasks = add_task_interval_variables(data, mdl)
    no_overlap_jobs(data, mdl, tasks)

    machine_sequence = add_sequence_variables(data, mdl, tasks)
    all_machines_same_sequence(data, machine_sequence, mdl)

    for i in range(data.num_machines):
        mdl.add(mdl.no_overlap(machine_sequence[i], data.setup[i]))

    minimize_makespan(data, mdl, tasks)

    return mdl
