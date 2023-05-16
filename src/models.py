import time
from itertools import product
from pathlib import Path
from typing import NamedTuple, Tuple, Union

import cplex
import gurobipy as grb
import matplotlib.pyplot as plt
import numpy as np
from cp import CP_MODELS
from mip.modelCplexMIP import MIPmodel_generation
from plotting import plot_schedule
from ProblemData import ProblemData


def main(
    path,
    time_limit,
    problem_type,
    model_type,
    solver,
    num_procs,
    out_dir,
):
    data = ProblemData.from_file(path, problem_type)
    name = path.stem

    kwargs = {
        "problem_type": problem_type,
        "name": name,
        "time_limit": time_limit,
        "num_procs": num_procs,
        "out_dir": out_dir,
    }

    time_start = time.perf_counter()

    if model_type == "mip":
        if solver == "cplex":
            model = cplex.Cplex()
            model = MIPmodel_generation(data, model, problem_type)
            x, y = CPLEX_MIP_solve(model, **kwargs)
        elif solver == "gurobi":
            model = cplex.Cplex()
            model = MIPmodel_generation(data, model, problem_type)
            model.write("model.lp")
            model = grb.read("model.lp")

            x, y = Gurobi_solve(model, **kwargs)
        else:
            raise ValueError(f"Unknown solver: {solver}")

    if model_type == "cp":
        model = CP_MODELS[problem_type](data)
        x, y = CPLEX_CP_solve(model, data=data, **kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    elapsed_time = round(time.perf_counter() - time_start, 3)

    try:
        gap_or_msg = round(100 * (y - x) / y) if y != 0 else 0
    except TypeError:
        gap_or_msg = "No solution"

    return (data.num_jobs, data.num_machines, elapsed_time, x, y, gap_or_msg)


def Gurobi_solve(model, problem_type, name, time_limit, num_procs, out_dir):
    model.setParam("MIPGapAbs", 0.99999)
    model.setParam("MIPGap", 0.0000)
    model.setParam("Timelimit", time_limit)
    model.setParam("Threads", num_procs)

    model.optimize()

    if model.status != 1:
        fname = "solution_MIP_Gurobi_{}_{}.txt".format(problem_type, name)
        with open(Path(out_dir) / fname, "w") as fh:
            fh.write(
                "\n MIP Gurobi {} - {} - ({} - {})".format(
                    problem_type,
                    name,
                    int(np.round(model.objbound)),
                    int(np.round(model.objVal)),
                )
            )
            for v in model.getVars():
                if v.x != 0:
                    if v.varName.startswith("C"):
                        fh.write("\n")
                        fh.write(v.varName)
                        fh.write(" ")
                        fh.write(str(np.round(v.x)))
        return int(np.round(model.objbound)), int(np.round(model.objVal))
    else:
        return "Infeasible", "Unkown"


def CPLEX_MIP_solve(model, problem_type, name, time_limit, num_procs, out_dir):
    model.parameters.timelimit.set(time_limit)
    model.parameters.mip.tolerances.absmipgap.set(0.99999)
    model.parameters.mip.tolerances.mipgap.set(0.00000)
    model.parameters.threads.set(num_procs)
    model.set_log_stream(None)
    model.set_error_stream(None)
    model.set_warning_stream(None)
    model.set_results_stream(None)
    model.solve()
    if (
        model.solution.get_status_string(status_code=None)
        != "integer infeasible"
        and model.solution.get_status_string(status_code=None)
        != "time limit exceeded, no integer solution"
    ):
        fname = "solution_MIP_CPLEX_{}_{}.txt".format(problem_type, name)
        with open(Path(out_dir) / fname, "w") as fh:
            fh.write(
                "\n MIP CPLEX {} - {} - ({} - {})".format(
                    problem_type,
                    name,
                    int(np.round(model.solution.MIP.get_best_objective())),
                    int(np.round(model.solution.get_objective_value())),
                )
            )

            for i, x in enumerate(model.solution.get_values()):
                if x != 0:
                    if model.variables.get_names(i).startswith("C"):
                        fh.write("\n")
                        fh.write(model.variables.get_names(i))
                        fh.write(" ")
                        fh.write(str(np.round(x)))
        return int(np.round(model.solution.MIP.get_best_objective())), int(
            np.round(model.solution.get_objective_value())
        )
    else:
        return "Infeasible", "Unkown"


Outcome = Union[int, str]


def CPLEX_CP_solve(
    model, problem_type, name, time_limit, num_procs, out_dir, data
) -> Tuple[Outcome, Outcome]:
    result = model.solve(
        TimeLimit=time_limit,
        Workers=num_procs,
        LogVerbosity="Terse",
        OptimalityTolerance=0.99,
        RelativeOptimalityTolerance=0.0,
    )

    if result.solution is None:
        return "Infeasible", "Unkown"

    lb = result.get_objective_bounds()[0]
    ub = result.get_objective_values()[0]

    fname = f"solution_CP_CPLEX_{problem_type}_{name}.txt"

    with open(Path(out_dir) / fname, "w") as fh:
        fh.write(f"\n CP {problem_type} - {name} - ({lb} - {ub})")

        for j in range(data.num_jobs):
            fh.write("\n")
            num_machines = data.num_machines

            for i in range(num_machines):
                if problem_type == "Parallelmachine":
                    var_name = "A_{}_{}".format(j, i)
                elif problem_type == "Unrelatedparallelmachines":
                    var_name = "T_{}".format(j)
                else:
                    var_name = "T_{}_{}".format(j, i)

                var = result.get_var_solution(var_name)
                x, y = var.get_end(), var.get_start()
                fh.write(f"{y} {x}\t")

    if problem_type == "Parallelmachine":
        schedule = result2schedule(data, result)
        plot_schedule(data, schedule)

    if problem_type == "Hybridflowshop":
        hfsresult2plot(data, result)

    if problem_type == "Complexdistributedflowshop":
        dpfsresult2plot(data, result)

    return lb, ub


class DFSItem(NamedTuple):
    job: int
    stage: int
    machine: int
    start: int
    duration: int


def result2schedule(data, result):
    schedule = []

    for machine in range(data.num_machines):
        job_start = []

        for job in range(data.num_jobs):
            var = result.get_var_solution(f"O_{job}_{machine}")

            if not var.is_absent():
                job_start.append((job, var.get_start()))

        sequence = [job for (job, *_) in sorted(job_start, key=lambda x: x[1])]
        schedule.append(sequence)

    return schedule


def hfsresult2schedules(data, result):
    """
    Extract the schedule for each stage in the HFS.
    """
    schedules = []

    for stage in range(data.num_stages):
        schedule = []

        for machine in range(data.machines[stage]):
            job_start = []

            for job in range(data.num_jobs):
                var = result.get_var_solution(f"A_{job}_{stage}_{machine}")

                if not var.is_absent():
                    job_start.append((job, var.get_start()))

            sequence = [
                job for job, _ in sorted(job_start, key=lambda x: x[1])
            ]
            schedule.append(sequence)

        schedules.append(schedule)

    return schedules


def hfsresult2plot(data, result):
    """
    Extract the schedule for each stage in the HFS.
    """
    schedule = []

    for job, stage in product(range(data.num_jobs), range(data.num_stages)):
        for machine in range(data.machines[stage]):
            var = result.get_var_solution(f"A_{job}_{stage}_{machine}")
            if var.is_absent():
                continue

            item = Item(job, stage, machine, var.get_start(), var.get_length())
            schedule.append(item)

    hfs_plot(data, schedule)


def hfs_plot(data, schedule, ax=None):
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

    plt.show()


class Item(NamedTuple):
    job: int
    factory: int
    machine: int
    start: int
    duration: int


def dpfsresult2plot(data, result):
    """
    Extracts the schedule for the DPFS and plots it.
    """
    schedule = []

    for i, k in product(range(data.num_machines), range(data.num_factories)):
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

    dpfs_plot(data, schedule)


def dpfs_plot(data, schedule, ax=None):
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
    plt.show()
