import itertools

import docplex.cp.model as docp


def storage_layer(data):
    """
    Create a storage layer model.

    A storage layer is a stage in which jobs do not need to be processed, i.e.,
    they do not have any processing times. Instead, the intervals are
    constrained by intra-stage constraints.

    Moreover, storage layers (in the application in compound feed production)
    must take into account multi-level product characteristics to avoid
    contamination of goods.

    The machine layout conists of a set of production lines, each of whch
    consists of one unrelated machine (i.e., storage) unit.

    This model uses the following variables:
    - $T_j$: interval variable for batch j
    - $Tp_j$: interval variable for product p
    - $Ap_{ji}$: interval assignment variable for product p on machine i
    - Sp_i$: sequence variable of product assignment variables on machine i

    We do not need to take into account batch assignment variables, since
    that is covered by the product assignment variables.
    """
    model = docp.CpoModel()

    batches_tasks = create_batch_tasks(model, data)
    tasks = create_product_tasks(model, data)
    assignments = create_product_assignments(model, data)
    sequences = create_sequence_variables(data, model, assignments)

    assign_one_line(data, model, tasks, assignments)
    assign_only_eligible_lines(data, model, assignments)

    products_span_batches(data, model, tasks, batches_tasks)
    no_overlap_on_machines(data, model, sequences)


def create_batch_tasks(model, data):
    """
    Creates a task interval variable $T_{b}$ for each batch $b \\in B$.
    """
    tasks = {j: model.interval_var(name=f"T_{j}") for j in data.jobs}
    return tasks


def create_product_tasks(model, data):
    """
    Creates a task interval variable $Tp_{pu}$ for each product $p \\in P$.
    """
    tasks = {j: model.interval_var(name=f"Tp_{j}") for j in data.products}
    return tasks


def create_product_assignments(model, data):
    """
    Creates an assignment interval variable $Tp_{pu}$ for each product
    $p \\in P$ and machine $i \\in M$.
    """
    assignments = {}

    for j, i in itertools.product(data.products, data.machines):
        name = f"Ap_{j}_{i}"
        assignments[(j, i)] = model.interval_var(name=name, optional=True)

    return assignments


def assign_one_line(data, model, tasks, assignments):
    """
    Assigns each product to exactly one machine.

    \\begin{equation}
        \\texttt{Alternative}(Tp_{p}, \\{Ap_{pi} : i \\in M \\})
        \\quad \\forall p \\in P.
    \\end{equation}
    """
    for j in data.products:
        intervals = [assignments[(j, i)] for i in data.machines]
        model.add(model.alternative(tasks[j], intervals))


def assign_only_eligible_lines(data, model, assign):
    """
    Assigns each product to only eligible machines.

    \\begin{equation}
        \\texttt{PresenceOf}(A_{pi}) = 0,
        \\quad \\forall i \\in M, p \\in E_{i}.
    \\end{equation}
    """
    for job, line in itertools.product(data.products, data.lines):
        if not data.eligible[job][line]:
            cons = model.presence_of(assign[(job, line)]) == 0
            model.add(cons)


def products_span_batches(data, model, product_tasks, batches_tasks):
    """
    Product interval variables span the corresponding batch interval variables.

    \\begin{equation}
        \\texttt{Span}(Tp_{p}, \\{T_{b} : b \\in B_p \\})
        \\quad \\forall p \\in P.
    \\end{equation}

    where $B_p$ denotes the set of batches that belong to product $p$.
    """
    for product in data.products:
        # TODO batches that correspond to product
        batches = [batches_tasks[batch] for batch in data.batches]
        product = product_tasks[product]
        cons = model.span(product_tasks, batches)

        model.add(cons)


def create_sequence_variables(data, model, assignments):
    """
    Creates a sequence variable $Sp_{i}$ for each machine $i \\in M$.
    """
    Sp = {}

    for i in data.machines:
        intervals = [assignments[(product, i)] for product in data.products]
        name = f"Sp_{i}"
        Sp[i] = model.sequence_var(intervals, name=name)

    return Sp


def no_overlap_on_machines(data, model, sequences):
    """
    No overlap on machines.

    \\begin{equation}
        \\texttt{NoOverlap}(Sp_{i}) \\quad \\forall i \\in M.
    \\end{equation}
    """
    for machine in data.machines:
        model.add(model.no_overlap(sequences[machine]))
