from itertools import product

import docplex.cp.model as docp

from .constraints import add_task_interval_variables
from .constraints.minimize_makespan import minimize_makespan


def ComplexDistributedFlowShop(data):
    mdl = docp.CpoModel()

    tasks = make_tasks_variables(data, mdl)
    _tasks = add_task_interval_variables(data, mdl, include_processing=False)
    sequences = make_sequence_variables(data, mdl, tasks)

    no_overlap_jobs(data, mdl, _tasks)

    assign_one_factory(data, mdl, tasks, _tasks)

    schedule_all_units_if_assigned(data, mdl, tasks)

    line_eligibility(data, mdl, tasks)

    no_overlap_machines(data, mdl, sequences)

    same_sequence_units(data, mdl, sequences)

    minimize_makespan(data, mdl, _tasks)

    return mdl


def make_tasks_variables(data, mdl):
    """
    Creates an interval variable for each job, machine and factory combination.
    """
    jobs = range(data.num_jobs)
    machines = range(data.num_machines)
    factories = range(data.num_factories)

    tasks = [[[] for _ in machines] for _ in jobs]

    for j, i in product(jobs, machines):
        for k in factories:
            name = f"A_{j}_{i}_{k}"
            proc = data.processing[j][i][k]  # unrelated processing times
            var = mdl.interval_var(name=name, optional=True, size=proc)
            tasks[j][i].append(var)

    return tasks


def make_sequence_variables(data, mdl, tasks):
    """
    Creates a sequence variable for each machine and factory combination.
    """
    seq_var = [
        [
            mdl.sequence_var(
                [tasks[j][i][k] for j in (range(data.num_jobs))],
                name=f"S_{i}_{k}",
            )
            for k in (range(data.num_factories))
        ]
        for i in (range(data.num_machines))
    ]
    return seq_var


def no_overlap_jobs(data, mdl, _tasks):
    """
    Adds a no overlap constraint for each job and machine combination, which
    ensures that a job can start on machine $i$ only when it's completed on
    machine $i-1$.

        NoOverlap(Task[j][i-1], Task[j][i])
    """
    for j, i in product(range(data.num_jobs), range(1, data.num_machines)):
        mdl.add(mdl.end_before_start(_tasks[j][i - 1], _tasks[j][i]))


def same_sequence_units(data, mdl, seq_var):
    """
    Ensures that the sequence of jobs on each machine is the same for each
    factory. It implements the constraint

        SameSequence(SeqVar[i][k], SeqVar[i+1][k])

    for each machine $i$ and factory $k$ combination.
    """
    for i, k in product(
        range(data.num_machines - 1), range(data.num_factories)
    ):
        mdl.add(mdl.same_sequence(seq_var[i][k], seq_var[i + 1][k]))


def line_eligibility(data, mdl, tasks):
    """
    Implements the line eligibility constraints on assignment variables.
    """
    for job, machine, factory in product(
        range(data.num_jobs),
        range(data.num_machines),
        range(data.num_factories),
    ):
        if not data.eligible[job][machine][factory]:
            cons = mdl.presence_of(tasks[job][machine][factory]) == 0
            mdl.add(cons)


def no_overlap_machines(data, mdl, seq_var):
    """
    Ensures that no two jobs are scheduled on the same machine at the same time.
    It implements the constraint

        NoOverlap(SeqVar[i][k], setup)

    for each machine $i$ and factory $k$ combination, where `setup` is a J-by-J
    matrix of setup times between jobs.
    """

    for i, k in product(range(data.num_machines), range(data.num_factories)):
        setup = data.setup[:, :, i, k]
        mdl.add(mdl.no_overlap(seq_var[i][k], setup))


def assign_one_factory(data, mdl, tasks, _tasks):
    """
    Ensures that each job is assigned to exactly one factory. It implements the
    constraint

        Alternative(Task[j][i], [Task[j][i][k] for k in range(num_factories)])

    for each job $j$ and machine $i$ combination.
    """
    for j, i in product(range(data.num_jobs), range(data.num_machines)):
        subexpr = [tasks[j][i][k] for k in (range(data.num_factories))]
        mdl.add(mdl.alternative(_tasks[j][i], subexpr))


def schedule_all_units_if_assigned(data, mdl, tasks):
    """
    Ensures that if a job is assigned to a factory, then all its units are
    scheduled. It implements the constraint

        PresenceOf(Task[j][i][k]) >= PresenceOf(Task[j][0][k])

    for each job $j$, machine $i$ and factory $k$ combination.
    """
    for j, i, k in product(
        range(data.num_jobs),
        range(1, data.num_machines),
        range(data.num_factories),
    ):
        mdl.add(
            mdl.presence_of(tasks[j][i][k]) >= mdl.presence_of(tasks[j][0][k])
        )
