from .base_model import base_model


def Tardinessflowshopmodel(data, mdl):
    mdl, tasks, _ = base_model(data, mdl)

    tardiness = []
    for j in range(data.jobs):
        late = mdl.end_of(tasks[j][data.machines - 1]) - data.due_dates[j]
        tardiness.append(mdl.max([late, 0]))

    mdl.add(mdl.minimize(mdl.sum(tardiness)))

    return mdl
