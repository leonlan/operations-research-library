import argparse
import os
import time
from functools import partial
from pathlib import Path
from typing import List, Union

import numpy as np
from tqdm.contrib.concurrent import process_map

import src
import src.plotting
from src.constants import ProblemType
from src.cp import CP_MODELS
from src.ProblemData import ProblemData


def main():
    parser = argparse.ArgumentParser(description="Description of your program")

    msg = "Path to the instances to solve."
    parser.add_argument("instances", type=str, nargs="+", help=msg)

    msg = "Scheduling problem type."
    parser.add_argument("--problem_type", type=ProblemType, help=msg)

    msg = "Time limit for the constriant programming solver in seconds."
    parser.add_argument("--time_limit", type=int, help=msg)

    msg = "Number of instances to solve in parallel."
    parser.add_argument("--num_procs", type=int, default=2)

    msg = "Number of processes to use by the constraint programming solver."
    parser.add_argument("--num_procs_solver", type=int, default=1, help=msg)

    msg = "Plot the solution?"
    parser.add_argument("--plot_dir", type=str, help=msg)

    benchmark(**vars(parser.parse_args()))


def solve(
    path: Union[str, os.PathLike],
    problem_type,
    time_limit: int,
    num_procs_solver: int,
    **kwargs,
):
    def cp_solver(model):
        return model.solve(
            TimeLimit=time_limit,
            Workers=num_procs_solver,
            LogVerbosity="Terse",
        )

    problem_type = problem_type.value
    data = ProblemData.from_file(path, problem_type)
    path = Path(path)
    name = path.stem

    time_start = time.perf_counter()

    model = CP_MODELS[problem_type](data)  # type: ignore
    result = cp_solver(model)

    if result.solution is None:
        return "Infeasible", "Unkown"

    lb = result.get_objective_bounds()[0]
    ub = result.get_objective_values()[0]

    if plot_dir := kwargs.get("plot_dir", ""):
        fname = Path(plot_dir) / f"{name}.pdf"
        plot(data, result, problem_type, fname)

    elapsed_time = round(time.perf_counter() - time_start, 3)

    return name, lb, ub, elapsed_time


def benchmark(instances: List[str], **kwargs):
    """
    Solves a list of instances, and prints a table with the results. Any
    additional keyword arguments are passed to ``solve()``.

    Parameters
    ----------
    instances
        Paths to the instances to solve.
    """

    maybe_mkdir(kwargs.get("plot_dir", ""))

    if len(instances) == 1:
        res = solve(instances[0], **kwargs)
        print(res)
        return

    func = partial(solve, **kwargs)
    func_args = sorted(instances)

    tqdm_kwargs = {
        "max_workers": kwargs.get("num_procs", 1),
        "unit": "instance",
    }
    data = process_map(func, func_args, **tqdm_kwargs)

    dtypes = [
        ("inst", "U37"),
        ("lb", int),
        ("ub", int),
        ("time", float),
    ]

    data = np.asarray(data, dtype=dtypes)
    headers = ["Instance", "LB", "UB", "Time (s)"]

    print("\n", tabulate(headers, data), "\n", sep="")
    print(f"      Avg. objective: {data['ub'].mean():.0f}")
    print(f"   Avg. run-time (s): {data['time'].mean():.2f}")


def plot(data, result, problem_type, fname):
    print(fname)
    if problem_type == "Unrelatedparallelmachines":
        src.plotting.upmresult2plot(data, result, fname)

    if problem_type == "Hybridflowshop":
        src.plotting.hfsresult2plot(data, result, fname)

    if problem_type == "Complexdistributedflowshop":
        src.plotting.dpfsresult2plot(data, result, fname)


def maybe_mkdir(where: str):
    if where:
        directory = Path(where)
        directory.mkdir(parents=True, exist_ok=True)


def tabulate(headers, rows) -> str:
    # These lengths are used to space each column properly.
    lengths = [len(header) for header in headers]

    for row in rows:
        for idx, cell in enumerate(row):
            lengths[idx] = max(lengths[idx], len(str(cell)))

    header = [
        "  ".join(f"{h:<{l}s}" for l, h in zip(lengths, headers)),
        "  ".join("-" * l for l in lengths),
    ]

    content = [
        "  ".join(f"{str(c):>{l}s}" for l, c in zip(lengths, row))
        for row in rows
    ]

    return "\n".join(header + content)


if __name__ == "__main__":
    main()
