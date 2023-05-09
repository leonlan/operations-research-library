import time
from pathlib import Path
from typing import Tuple, Union

import cplex
import gurobipy as grb
import numpy as np
from cp import CP_MODELS
from mip.modelCplexMIP import MIPmodel_generation
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
    msol = model.solve(
        TimeLimit=time_limit,
        Workers=num_procs,
        LogVerbosity="Terse",
        OptimalityTolerance=0.99,
        RelativeOptimalityTolerance=0.0,
    )

    if msol.solution.is_empty():
        return "Infeasible", "Unkown"

    lb = msol.get_objective_bounds()[0]
    ub = msol.get_objective_values()[0]

    fname = f"solution_CP_CPLEX_{problem_type}_{name}.txt"

    with open(Path(out_dir) / fname, "w") as fh:
        fh.write(f"\n CP {problem_type} - {name} - ({lb} - {ub})")

        for j in range(data.num_jobs):
            fh.write("\n")
            num_machines = data.num_machines

            for i in range(num_machines):
                var_name = (
                    "T_{}_{}".format(j, i)
                    if problem_type != "Parallelmachine"
                    else "A_{}_{}".format(j, i)
                )
                var = msol.get_var_solution(var_name)
                x, y = var.get_end(), var.get_start()
                fh.write(f"{y} {x}\t")

    return lb, ub
