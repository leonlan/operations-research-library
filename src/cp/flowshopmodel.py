from .base_model import base_model
from .constraints.minimize_makespan import minimize_makespan


def flowshopmodel(data):
    mdl, tasks, _ = base_model(data)
    minimize_makespan(data, mdl, tasks)

    return mdl
