from .base_model import base_model


def TCTflowshopmodel(data, mdl):
    mdl, tasks, _ = base_model(data, mdl)

    completion_times = [mdl.end_of(tasks[j][-1]) for j in range(data.num_jobs)]
    mdl.add(mdl.minimize(mdl.sum(completion_times)))

    return mdl
