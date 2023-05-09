from pathlib import Path
from typing import Optional

import models
import typer
from constants import ProblemType


def main(
    datas: list[str],
    problem_type: ProblemType = typer.Option(
        ProblemType.PARALLEL_MACHINE, case_sensitive=False
    ),
    model_type: str = "cp",
    time_limit: int = 3,
    solver: str = "cplex",
    num_procs: int = 1,
    out_dir: Optional[str] = "tmp/",
):
    for where in datas:
        path = Path(where)
        num_jobs, num_stages, time, lb, ub, gap = models.main(
            path,
            time_limit,
            problem_type.value,
            model_type.lower(),
            solver.lower(),
            num_procs,
            out_dir,
        )

        x = f"{out_dir}/{path.stem}.txt"
        with open(x, "w") as fh:
            result = f"{problem_type}\t{solver}\t{model_type}\t{path.stem}\t{num_jobs}\t{num_stages}\t{lb}\t{ub}\t{gap}\t{time}"
            fh.write(result)

            print(result)


if __name__ == "__main__":
    typer.run(main)
