from itertools import product
from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np


class DFSItem(NamedTuple):
    job: int
    stage: int
    machine: int
    start: int
    duration: int


def dpfsresult2plot(data, result, fname):
    """
    Extracts the schedule for the DPFS and plots it.
    """
    schedule = []

    for i, k in product(data.machines, range(data.num_factories)):
        # Only get the first machine because we assume permutation flow shops.
        seq_var = result.get_var_solution(f"S_{i}_{k}")

        for interval_var in seq_var.get_interval_variables():
            name = interval_var.get_name()
            job = int(name.split("_")[1])
            item = DFSItem(
                job,
                k,
                i,
                interval_var.get_start(),
                interval_var.get_length(),
            )
            schedule.append(item)

    dpfs_plot(data, schedule, fname)


def dpfs_plot(data, schedule, fname=None, ax=None):
    _, ax = plt.subplots(data.num_factories, 1, figsize=(10, 10))

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

    for factory in range(data.num_factories):
        ax[factory].set_ylabel(f"Factory {factory+1}")

        # Invert y-axis to have the first machine at the top.
        ax[factory].set_ylim(ax[factory].get_ylim()[::-1])

    plt.xlabel("Time")

    if fname is not None:
        plt.savefig(fname, bbox_inches="tight")
    else:
        plt.show()
