from .base_model import base_model
from .constraints.minimize_total_tardiness import minimize_total_tardiness


def TardinessFlowShop(data):
    model, tasks, _ = base_model(data)
    minimize_total_tardiness(data, model, tasks)
    return model
