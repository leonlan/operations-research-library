from typing import List

import matplotlib.pyplot as plt


def upmresult2plot(data, result):
    schedule = result2schedule(data, result)
    plot_schedule(data, schedule)


def result2schedule(data, result):
    schedule = []

    for machine in range(data.num_machines):
        job_start = []

        for job in range(data.num_jobs):
            var = result.get_var_solution(f"A_{job}_{machine}")

            if not var.is_absent():
                job_start.append((job, var.get_start()))

        sequence = [job for (job, *_) in sorted(job_start, key=lambda x: x[1])]
        schedule.append(sequence)

    return schedule


def plot_schedule(data, schedule: List[List[int]], ax=None):
    """
    Plots a schedule.
    """
    if ax is None:
        _, ax = plt.subplots()

    bars = []

    for machine, sequence in enumerate(schedule):
        start = 0

        for seq_idx, job in enumerate(sequence):
            if seq_idx > 0:
                prev_job = sequence[seq_idx - 1]
                try:
                    start += data.setup[machine][prev_job][job]
                except IndexError:
                    pass

            duration = data.processing[job][machine]
            bars.append((machine, job, start, duration))
            start += duration

    for machine, job, start, duration in bars:
        bar = ax.barh(machine, width=duration, left=start, label=job)
        ax.bar_label(bar, label_type="center")

    plt.yticks(range(data.num_machines), range(1, data.num_machines + 1))
    plt.xticks()
    plt.xlabel("Time")
    plt.ylabel("Machine")

    plt.show()
