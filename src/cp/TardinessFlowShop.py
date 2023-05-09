from .base_model import base_model
from .constraints.minimize_total_tardiness import minimize_total_tardiness


def TardinessFlowShop(data):
    mdl, tasks, _ = base_model(data)
    minimize_total_tardiness(data, mdl, tasks)
    return mdl
