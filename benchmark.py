import time
from pathlib import Path
from typing import Tuple, Union

import typer

import src
import src.plotting
from src.constants import ProblemType
from src.cp import CP_MODELS
from src.ProblemData import ProblemData


def main(
    datas: list[str],
    problem_type: ProblemType = typer.Option(
        ProblemType.PARALLEL_MACHINE, case_sensitive=False
    ),
    time_limit: int = 3,
    num_procs: int = 1,
):
    for where in datas:
        path = Path(where)
        num_jobs, num_stages, time, lb, ub, gap = solve(
            path, time_limit, problem_type.value, num_procs
        )


def solve(
    path,
    time_limit,
    problem_type,
    num_procs,
):
    data = ProblemData.from_file(path, problem_type)
    name = path.stem

    kwargs = {
        "problem_type": problem_type,
        "name": name,
        "time_limit": time_limit,
        "num_procs": num_procs,
    }

    time_start = time.perf_counter()

    model = CP_MODELS[problem_type](data)
    x, y = CPLEX_CP_solve(model, data=data, **kwargs)

    elapsed_time = round(time.perf_counter() - time_start, 3)

    try:
        gap_or_msg = round(100 * (y - x) / y) if y != 0 else 0
    except TypeError:
        gap_or_msg = "No solution"

    return (data.num_jobs, data.num_machines, elapsed_time, x, y, gap_or_msg)


Outcome = Union[int, str]


def CPLEX_CP_solve(
    model, problem_type, name, time_limit, num_procs, data
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

    if problem_type == "Unrelatedparallelmachines":
        src.plotting.upmresult2plot(data, result)

    if problem_type == "Hybridflowshop":
        src.plotting.hfsresult2plot(data, result)

    if problem_type == "Complexdistributedflowshop":
        src.plotting.dpfsresult2plot(data, result)

    return lb, ub


if __name__ == "__main__":
    typer.run(main)
