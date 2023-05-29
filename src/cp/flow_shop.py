import docplex.cp.model as docp

from src.ProblemData import ProblemData

from .constraints import (
    create_sequence_variables,
    create_task_interval_variables,
    minimize_makespan,
    minimize_total_completion_times,
    minimize_total_tardiness,
    no_overlap_between_machines,
    no_overlap_on_machines,
    same_sequence_on_each_machine,
)


def flow_shop(
    data: ProblemData, objective: str = "makespan", include_setup: bool = False
) -> docp.CpoModel:
    """
    Creates a CP model for the flow shop problem. This model can be configured
    to solve a flow shop problem with or without setup times, and with
    different objective functions.

    Parameters
    ----------
    data
        The problem data.
    objective
        The objective function to minimize. The default is "makespan".
    include_setup
        Whether to use the setup times or not. The default is False. If set,
        then the problem data must have a ``setup`` field.

    Returns
    -------
    CpoModel
        The CP model for a flow shop problem.
    """
    model = docp.CpoModel()

    # Variables
    tasks = create_task_interval_variables(data, model)
    no_overlap_between_machines(data, model, tasks)

    # Constraints
    sequences = create_sequence_variables(data, model, tasks)
    no_overlap_on_machines(data, model, sequences, include_setup)
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
