from pathlib import Path

import models
import typer
from constants import ProblemType


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
        num_jobs, num_stages, time, lb, ub, gap = models.main(
            path, time_limit, problem_type.value, num_procs
        )


if __name__ == "__main__":
    typer.run(main)
