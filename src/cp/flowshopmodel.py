from .base_model import base_model
from .constraints.minimize_makespan import minimize_makespan


def flowshopmodel(data, mdl):
    mdl, tasks, _ = base_model(data, mdl)
    minimize_makespan(data, mdl, tasks)

    return mdl
