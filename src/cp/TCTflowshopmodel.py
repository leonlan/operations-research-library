from .base_model import base_model
from .constraints.minimize_completion_times import minimize_completion_times


def TCTflowshopmodel(data):
    mdl, tasks, _ = base_model(data)

    minimize_completion_times(data, mdl, tasks)
    return mdl
