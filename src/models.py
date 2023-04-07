import time
from pathlib import Path

import cplex
import docplex.cp.model as docp
import gurobipy as grb
import modelCplexCP
import modelCplexMIP
import numpy as np
from Instance import Instance


def main(
    path,
    time_limit,
    problemType,
    modelType,
    solver,
    NThreads,
    output,
):
    instance = Instance.from_file(path, problemType)
    name = path.stem

    time_start = time.perf_counter()

    if modelType == "mip":
        if solver == "cplex":
            model = cplex.Cplex()
            model = modelCplexMIP.MIPmodel_generation(
                instance, model, problemType
            )
            x, y = CPLEX_MIP_solve(
                model,
                problemType,
                name,
                time_limit,
                NThreads,
                output,
            )
        if solver == "gurobi":
            model = cplex.Cplex()
            model = modelCplexMIP.MIPmodel_generation(
                instance, model, problemType
            )
            model.write("model.lp")
            model = grb.read("model.lp")
            x, y = Gurobi_solve(
                model,
                problemType,
                name,
                time_limit,
                NThreads,
                output,
            )

    if modelType == "cp":
        if solver == "cplex":
            model = docp.CpoModel()
            model = modelCplexCP.CPmodel_generation(
                instance, model, problemType
            )
            x, y = CPLEX_CP_solve(
                model,
                problemType,
                name,
                time_limit,
                NThreads,
                instance,
                output,
            )

    time_elapsed = np.round(time.perf_counter() - time_start, 3)

    if isinstance(x, int) is True or isinstance(x, float) is True:
        if y != 0:
            return (
                instance.n,
                instance.g,
                time_elapsed,
                x,
                y,
                np.round(100 * (y - x) / y),
            )
        else:
            return instance.n, instance.g, time_elapsed, x, y, 0
    else:
        return instance.n, instance.g, time_elapsed, x, y, "No solution"


def Gurobi_solve(model, problemType, name, time_limit, NThreads, output):
    model.setParam("MIPGapAbs", 0.99999)
    model.setParam("MIPGap", 0.0000)
    model.setParam("Timelimit", time_limit)
    model.setParam("Threads", NThreads)

    model.optimize()

    if model.status != 1:
        fname = "solution_MIP_Gurobi_{}_{}.txt".format(problemType, name)
        with open(Path(output) / fname, "w") as fh:
            fh.write(
                "\n MIP Gurobi {} - {} - ({} - {})".format(
                    problemType,
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


def CPLEX_MIP_solve(model, problemType, name, time_limit, NThreads, output):
    model.parameters.timelimit.set(time_limit)
    model.parameters.mip.tolerances.absmipgap.set(0.99999)
    model.parameters.mip.tolerances.mipgap.set(0.00000)
    model.parameters.threads.set(NThreads)
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
        fname = "solution_MIP_CPLEX_{}_{}.txt".format(problemType, name)
        with open(Path(output) / fname, "w") as fh:
            fh.write(
                "\n MIP CPLEX {} - {} - ({} - {})".format(
                    problemType,
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


def CPLEX_CP_solve(
    model, problemType, name, time_limit, NThreads, instance, output
):
    msol = model.solve(
        TimeLimit=time_limit,
        Workers=NThreads,
        LogVerbosity="Quiet",
        WarningLevel=0,
        OptimalityTolerance=0.99,
        RelativeOptimalityTolerance=0.0,
    )

    if msol.solution.is_empty() is False:
        fname = "solution_CP_CPLEX_{}_{}.txt".format(problemType, name)
        with open(Path(output) / fname, "w") as fh:
            fh.write(
                "\n CP {} - {} - ({} - {})".format(
                    problemType,
                    name,
                    int(np.round(msol.get_objective_bounds()[0])),
                    int(np.round(msol.get_objective_values()[0])),
                )
            )
            if problemType != "Parallelmachine":
                for j in range(instance.n):
                    fh.write("\n")
                    q = instance.g
                    if problemType != "Parallelmachine":
                        for i in range(q):
                            var = msol.get_var_solution("T_{}_{}".format(j, i))
                            x = var.get_end()
                            y = var.get_start()
                            var.get_value()
                            fh.write(str(y))
                            fh.write(" ")
                            fh.write(str(x))
                            fh.write("\t")
                    else:
                        for i in range(q):
                            var = msol.get_var_solution("A_{}_{}".format(j, i))
                            x = var.get_end()
                            y = var.get_start()
                            var.get_value()
                            fh.write(str(y))
                            fh.write(" ")
                            fh.write(str(x))
                            fh.write("\t")

        return int(np.round(msol.get_objective_bounds()[0])), int(
            np.round(msol.get_objective_values()[0])
        )
    else:
        return "Infeasible", "Unkown"
