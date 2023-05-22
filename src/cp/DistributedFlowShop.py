from itertools import product

import docplex.cp.model as docp

from .constraints import create_task_interval_variables
from .constraints.minimize_makespan import minimize_makespan


def DistributedFlowShop(data):
    model = docp.CpoModel()

    tasks = make_tasks_variables(data, model)

    _tasks = create_task_interval_variables(data, model)
    seq_var = make_sequence_variables(data, model, tasks)

    no_overlap_jobs(data, model, _tasks)

    assign_one_factory(data, model, tasks, _tasks)

    schedule_all_units_if_assigned(data, model, tasks)

    no_overlap_machines(data, model, seq_var)

    same_sequence_units(data, model, seq_var)

    minimize_makespan(data, model, _tasks)

    return model


def make_tasks_variables(data, model):
    """
    Creates an interval variable for each job, machine and factory combination.
    """
    jobs = data.jobs
    machines = data.machines
    factories = range(data.num_factories)

    tasks = [[[] for _ in machines] for _ in jobs]

    for j, i in product(jobs, machines):
        for k in factories:
            var = model.interval_var(
                name=f"A_{j}_{i}_{k}",
                optional=True,
                size=data.processing[j][i],
            )
            tasks[j][i].append(var)

    return tasks


def make_sequence_variables(data, model, tasks):
    """
    Creates a sequence variable for each machine and factory combination.
    """
    seq_var = [
        [
            model.sequence_var([tasks[j][i][k] for j in (data.jobs)])
            for k in (range(data.num_factories))
        ]
        for i in (data.machines)
    ]
    return seq_var


def no_overlap_jobs(data, model, _tasks):
    """
    Adds a no overlap constraint for each job and machine combination, which
    ensures that a job can start on machine $i$ only when it's completed on
    machine $i-1$.

        NoOverlap(Task[j][i-1], Task[j][i])
    """
    for j, i in product(data.jobs, range(1, data.num_machines)):
        model.add(model.end_before_start(_tasks[j][i - 1], _tasks[j][i]))


def same_sequence_units(data, model, seq_var):
    """
    Ensures that the sequence of jobs on each machine is the same for each
    factory. It implements the constraint

        SameSequence(SeqVar[i][k], SeqVar[i+1][k])

    for each machine $i$ and factory $k$ combination.
    """
    for i, k in product(
        range(data.num_machines - 1), range(data.num_factories)
    ):
        model.add(model.same_sequence(seq_var[i][k], seq_var[i + 1][k]))


def no_overlap_machines(data, model, seq_var):
    """
    Ensures that no two jobs are scheduled on the same machine at the same time.
    It implements the constraint

        NoOverlap(SeqVar[i][k])

    for each machine $i$ and factory $k$ combination.
    """

    for i, k in product(data.machines, range(data.num_factories)):
        model.add(model.no_overlap(seq_var[i][k]))


def assign_one_factory(data, model, tasks, _tasks):
    """
    Ensures that each job is assigned to exactly one factory. It implements the
    constraint

        Alternative(Task[j][i], [Task[j][i][k] for k in range(num_factories)])

    for each job $j$ and machine $i$ combination.
    """
    for j, i in product(data.jobs, data.machines):
        subexpr = [tasks[j][i][k] for k in (range(data.num_factories))]
        model.add(model.alternative(_tasks[j][i], subexpr))


def schedule_all_units_if_assigned(data, model, tasks):
    """
    Ensures that if a job is assigned to a factory, then all its units are
    scheduled. It implements the constraint

        PresenceOf(Task[j][i][k]) >= PresenceOf(Task[j][0][k])

    for each job $j$, machine $i$ and factory $k$ combination.
    """
    for j, i, k in product(
        data.jobs,
        range(1, data.num_machines),
        range(data.num_factories),
    ):
        model.add(
            model.presence_of(tasks[j][i][k])
            >= model.presence_of(tasks[j][0][k])
        )
