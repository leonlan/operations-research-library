from itertools import product

import docplex.cp.model as docp

from .constraints import add_task_interval_variables
from .constraints.minimize_makespan import minimize_makespan


def DistributedFlowShop(data):
    mdl = docp.CpoModel()

    jobs = range(data.num_jobs)
    stages = range(data.num_machines)
    factories = range(data.num_factories)

    # fmt: off
    # TODO how to make this more legible?
    tasks = [[[mdl.interval_var(name=f"A_{j}{i}{k}",
                                optional=True,
                                size=data.processing[j][i])
               for k in factories] for i in stages] for j in jobs]
    # fmt: on

    _tasks = add_task_interval_variables(data, mdl)

    for j, i in product(jobs, stages):
        subexpr = [tasks[j][i][k] for k in factories]
        mdl.add(mdl.alternative(_tasks[j][i], subexpr))

    for j, i, k in product(jobs, range(1, data.num_machines), factories):
        mdl.add(
            mdl.presence_of(tasks[j][i][k]) >= mdl.presence_of(tasks[j][0][k])
        )

    seq_var = [
        [mdl.sequence_var([tasks[j][i][k] for j in jobs]) for k in factories]
        for i in stages
    ]

    for i, k in product(stages, factories):
        mdl.add(mdl.no_overlap(seq_var[i][k]))

    for i, k in product(range(data.num_machines - 1), factories):
        mdl.add(mdl.same_sequence(seq_var[i][k], seq_var[i + 1][k]))

    for j, i in product(jobs, range(1, data.num_machines)):
        mdl.add(mdl.end_before_start(_tasks[j][i - 1], _tasks[j][i]))

    minimize_makespan(data, mdl, _tasks)

    return mdl
