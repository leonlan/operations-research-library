from itertools import product

import docplex.cp.model as docp

from src.ProblemData import ProblemData


def distributed_flow_shop(data: ProblemData) -> docp.CpoModel:
    """
    Creates a CP model for the distributed flow shop problem (DFSP).
    """
    model = docp.CpoModel()

    tasks = create_tasks_variables(data, model)
    assign = create_assignment_variables(data, model)
    sequences = create_sequence_variables(data, model, assign)

    minimize_makespan(data, model, tasks)

    assign_one_line(data, model, assign, tasks)
    assign_only_eligible_lines(data, model, assign)
    assign_to_all_units_of_single_line(data, model, assign)

    no_overlap_between_units(data, model, tasks)
    no_overlap_on_unit(data, model, sequences)
    same_sequence_on_each_unit(data, model, sequences)

    return model


def create_tasks_variables(data, model):
    """
    Creates a task interval variable $T_{ju}$ for each job $j \\in J$ and
    unit $u \\in U$.
    """
    tasks = {}

    for j, u in product(data.jobs, data.units):
        tasks[(j, u)] = model.interval_var(name=f"T_{j}_{u}")

    return tasks


def create_assignment_variables(data, model):
    """
    Creates an assignment interval variable $A_{jul}$ for each job $j \\in J$,
    unit $u \\in U$, and line $l \\in L$.
    """
    assign = {}

    for j, u, l in product(data.jobs, data.units, data.lines):
        name = f"A_{j}_{u}_{l}"
        size = data.processing[j][u][l]
        var = model.interval_var(name=name, optional=True, size=size)
        assign[(j, u, l)] = var

    return assign


def create_sequence_variables(data, model, assign):
    """
    Creates a sequence variable $S_{ul}$ for each unit $u \\in U$ and
    line $l \\in L$.
    """
    sequences = {}

    for u, l in product(data.units, data.lines):
        name = f"S_{u}_{l}"
        subexpr = [assign[(j, u, l)] for j in data.jobs]
        sequences[(u, l)] = model.sequence_var(subexpr, name=name)

    return sequences


def minimize_makespan(data, model, tasks):
    """
    Minimizes the makespan of the schedule. It implements the objective
    function:

    \\begin{equation}
        \\min \\max_{j \\in J} \\texttt{EndOf}(T_{j|M|}).
    \\end{equation}
    """
    last = data.num_units
    completion_times = [model.end_of(tasks[(j, last - 1)]) for j in data.jobs]
    makespan = model.max(completion_times)
    model.add(model.minimize(makespan))


def no_overlap_between_units(data, model, tasks):
    """
    Adds a no-overlap constraint for each job and unit combination, which
    ensures that a job can start on unit $u$ only when it's completed on
    unit $u-1$.

    \\begin{equation}
        \\texttt{NoOverlap}(T_{j, i-1}, T_{ju}),
        \\quad \\forall j \\in J, u \\in U \\setminus {1}.
    \\end{equation}
    """
    for j, u in product(data.jobs, range(1, data.num_units)):
        cons = model.end_before_start(tasks[(j, u - 1)], tasks[(j, u)])
        model.add(cons)


def same_sequence_on_each_unit(data, model, sequences):
    """
    Ensures that the sequence of jobs is the same for all units of the same
    production line.

    \\begin{equation}
        \\texttt{SameSequence}(S_{ul}, S_{u+1,l}),
        \\quad \\forall u \\in U, l \\in L.
    \\end{equation}
    """
    for u, l in product(range(data.num_units - 1), data.lines):
        cons = model.same_sequence(sequences[(u, l)], sequences[(u + 1, l)])
        model.add(cons)


def assign_only_eligible_lines(data, model, assign):
    """
    Implements the line eligibility constraints on assignment variables.

    \\begin{equation}
        \\texttt{PresenceOf}(A_{jul}) = 0,
        \\quad \\forall u \\in U, l \\in L, j \\in E_{ul}.
    \\end{equation}
    """
    for job, unit, line in product(data.jobs, data.units, data.lines):
        if not data.eligible[job][unit][line]:
            cons = model.presence_of(assign[(job, unit, line)]) == 0
            model.add(cons)


def no_overlap_on_unit(data, model, seq_var):
    """
    Ensures that no two jobs are scheduled on the same unit at the same
    time. It implements the constraint

    \\begin{equation}
        \\texttt{NoOverlap}(S_{ul}, sdst_{ul}),
        \\quad \\forall u \\in U, l \\in L,
    \\end{equation}

    where $sdst_{ul}$ is a $J$-by-$J$ matrix of sequence-dependent setup times
    on unit $u$ and line $l$.
    """

    for u, l in product(data.units, data.lines):
        setup = data.setup[:, :, u, l]
        model.add(model.no_overlap(seq_var[(u, l)], setup))


def assign_one_line(data, model, assign, tasks):
    """
    Ensures that each job is assigned to exactly one line. It implements the
    constraint

    \\begin{equation}
        \\texttt{Alternative}(T_{ju}, \\{A_{jul} : l \\in L \\})
        \\quad \\forall j \\in J.
    \\end{equation}
    """
    for j, u in product(data.jobs, data.units):
        assign_vars = [assign[(j, u, k)] for k in data.lines]
        model.add(model.alternative(tasks[(j, u)], assign_vars))


def assign_to_all_units_of_single_line(data, model, assign):
    """
    Ensures that if a job is assigned to a line, then all its units are
    scheduled. It implements the constraint

    \\begin{equation}
        \\texttt{PresenceOf}(A_{jul}) \\geq \\texttt{PresenceOf}(A_{j0l})
        \\quad \\forall j \\in J, u \\in U \\setminus {1}, l \\in L.
    \\end{equation}
    """
    for j, u, l in product(data.jobs, range(1, data.num_units), data.lines):
        other = model.presence_of(assign[(j, u, l)])
        first = model.presence_of(assign[(j, 0, l)])
        model.add(other >= first)
