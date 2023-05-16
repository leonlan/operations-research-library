import argparse
import time
from functools import partial
from pathlib import Path
from typing import List

import numpy as np
from tqdm.contrib.concurrent import process_map

import src
import src.plotting
from src.constants import ProblemType
from src.cp import CP_MODELS
from src.ProblemData import ProblemData


def main():
    parser = argparse.ArgumentParser(description="Description of your program")
    parser.add_argument(
        "instances",
        metavar="instance",
        type=str,
        nargs="+",
        help="A list of data to process",
    )
    parser.add_argument(
        "--problem_type",
        type=ProblemType,
        default=ProblemType.PARALLEL_MACHINE,
        help="Type of the problem to solve (default: PARALLEL_MACHINE)",
    )
    parser.add_argument(
        "--time_limit",
        type=int,
        default=3,
        help="Time limit for benchmarking (default: 3)",
    )
    parser.add_argument(
        "--num_procs",
        type=int,
        default=2,
        help="Number of processes to run at a time (default: 1)",
    )
    parser.add_argument(
        "--num_procs_cp",
        type=int,
        default=1,
        help="Number of processes for copying (default: 1)",
    )
    parser.add_argument("--plot", type=bool)

    benchmark(**vars(parser.parse_args()))


def solve(
    path,
    problem_type,
    time_limit,
    num_procs,
    num_procs_cp,
    **kwargs,
):
    problem_type = problem_type.value
    data = ProblemData.from_file(path, problem_type)
    path = Path(path)
    name = path.stem

    kwargs = {
        "time_limit": time_limit,
        "num_procs": num_procs_cp,
    }

    time_start = time.perf_counter()

    model = CP_MODELS[problem_type](data)
    result = cp_solver(model, **kwargs)

    if result.solution is None:
        return "Infeasible", "Unkown"

    lb = result.get_objective_bounds()[0]
    ub = result.get_objective_values()[0]

    if kwargs.get("plot", False):
        plot(data, result, problem_type)

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


def cp_solver(model, time_limit, num_procs):
    return model.solve(
        TimeLimit=time_limit,
        Workers=num_procs,
        LogVerbosity="Terse",
        OptimalityTolerance=0.99,
        RelativeOptimalityTolerance=0.0,
    )


def plot(data, result, problem_type):
    if problem_type == "Unrelatedparallelmachines":
        src.plotting.upmresult2plot(data, result)

    if problem_type == "Hybridflowshop":
        src.plotting.hfsresult2plot(data, result)

    if problem_type == "Complexdistributedflowshop":
        src.plotting.dpfsresult2plot(data, result)


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
