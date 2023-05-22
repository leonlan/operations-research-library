from itertools import product
from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np


def hfsresult2plot(data, result, fname):
    """
    Extract the schedule for each stage in the HFS.
    """
    schedule = []

    for job, stage in product(data.jobs, data.stages):
        for machine in range(data.machines[stage]):
            var = result.get_var_solution(f"A_{job}_{stage}_{machine}")
            if var.is_absent():
                continue

            item = Item(job, stage, machine, var.get_start(), var.get_length())
            schedule.append(item)

    hfs_plot(data, schedule, fname)


def hfsresult2schedules(data, result):
    """
    Extract the schedule for each stage in the HFS.
    """
    schedules = []

    for stage in data.stages:
        schedule = []

        for machine in range(data.machines[stage]):
            job_start = []

            for job in data.jobs:
                var = result.get_var_solution(f"A_{job}_{stage}_{machine}")

                if not var.is_absent():
                    job_start.append((job, var.get_start()))

            sequence = [
                job for job, _ in sorted(job_start, key=lambda x: x[1])
            ]
            schedule.append(sequence)

        schedules.append(schedule)

    return schedules


def hfs_plot(data, schedule, fname=None, ax=None):
    _, ax = plt.subplots(data.num_stages, 1, figsize=(10, 10))

    def get_completion_time(item):
        return item.start + item.duration

    # Defining custom 'xlim' and 'ylim' values.
    latest = max(schedule, key=get_completion_time)
    custom_xlim = (0, get_completion_time(latest))

    # Setting the values for all axes.
    plt.setp(ax, xlim=custom_xlim)

    # Color per job
    hsv = plt.get_cmap("hsv")
    colors = hsv(np.linspace(0, 1.0, data.num_jobs))

    for job, stage, machine, start, duration in schedule:
        ax[stage].barh(machine, width=duration, left=start, color=colors[job])
        ax[stage].text(start + duration / 4, machine, job, va="center")

    plt.xlabel("Time")
    plt.ylabel("Machine")

    if fname is not None:
        plt.savefig(fname, bbox_inches="tight")
    else:
        plt.show()


class Item(NamedTuple):
    job: int
    factory: int
    machine: int
    start: int
    duration: int
