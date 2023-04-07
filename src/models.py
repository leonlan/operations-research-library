import time
from pathlib import Path

import cplex
import gurobipy as grb
import modelCplexCP
import modelCplexMIP
import modelGoogleCP
import modelGoogleMIP
import numpy as np
from docplex.cp.model import *
from Instance import Instance
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model


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

    if modelType == "MIP":
        if solver == "CPLEX":
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
        if solver == "Gurobi":
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
        if solver == "Google":
            model = pywraplp.Solver.CreateSolver("SCIP")
            model = modelGoogleMIP.MIPmodel_generation(
                instance, model, problemType
            )
            x, y = Google_MIP_solve(
                model,
                problemType,
                name,
                time_limit,
                NThreads,
                output,
            )
        if solver == "Xpress":
            model = cplex.Cplex()
            model = modelCplexMIP.MIPmodel_generation(
                instance, model, problemType
            )
            model.write("model.lp")
            model = xp.problem()
            model.read("model", "l")
            x, y = Xpress_MIP_solve(
                model,
                problemType,
                name,
                time_limit,
                NThreads,
                output,
            )

    if modelType == "CP":
        if solver == "CPLEX":
            model = CpoModel()
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
        if solver == "Google":
            model = cp_model.CpModel()
            model = modelGoogleCP.CPmodel_generation(
                instance, model, problemType
            )
            x, y = Google_CP_solve(
                model,
                problemType,
                name,
                time_limit,
                NThreads,
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


####### Solve the MIP problem by Xpress ########
def Xpress_MIP_solve(model, problemType, name, time_limit, NThreads, output):
    model.controls.outputlog = 0
    model.setControl("maxtime", -time_limit)
    model.solve()
    if model.getProbStatusString() in ["mip_optimal", "mip_solution"]:
        return int(np.round(model.attributes.bestbound)), int(
            np.round(model.attributes.mipobjval)
        )
    else:
        return "Infeasible", "Unkown"


####### Solve the MIP problem by Google ########
def Google_MIP_solve(model, problemType, name, time_limit, NThreads, output):
    model.SetTimeLimit(time_limit * 1000)
    status = model.Solve()
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        return np.round(model.Objective().BestBound()), np.round(
            model.Objective().Value()
        )
    else:
        return "Infeasible", "Unkown"


####### Solve the CP problem by Google ########
def Google_CP_solve(model, problemType, name, time_limit, NThreads, output):
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(
        model
    )  # 0 optimal, 1 feasible, 2 infeasible, 3 unbounded, 4 abnoral, 5 not_solved
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        return np.round(solver.BestObjectiveBound()), np.round(
            solver.ObjectiveValue()
        )
    else:
        return "Infeasible", "Unkown"


####### Solve the MIP problem by Gurobi ########
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


####### Solve the MIP problem by CPLEX ########
def CPLEX_MIP_solve(model, problemType, name, time_limit, NThreads, output):
    model.parameters.timelimit.set(time_limit)
    model.parameters.mip.tolerances.absmipgap.set(0.99999)
    model.parameters.mip.tolerances.mipgap.set(0.00000)
    model.parameters.threads.set(NThreads)
    model.set_log_stream(None)
    model.set_error_stream(None)
    model.set_warning_stream(None)
    model.set_results_stream(None)
    # model.write('..\\LPs\\{}\\model_{}_{}.lp'.format(problemType,problemType,name))
    # comment to generate only LP files
    # model.write('model.lp')
    # model.parameters.tune_problem_set(filenames=["model.lp"])
    model.solve()
    if (
        model.solution.get_status_string(status_code=None)
        != "integer infeasible"
        and model.solution.get_status_string(status_code=None)
        != "time limit exceeded, no integer solution"
    ):
        with open(
            "{}\\solution_MIP_CPLEX_{}_{}.txt".format(
                output, problemType, name
            ),
            "w",
        ) as fh:
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
    # end comment


####### Solve the CP problem by DOCPLEX ########
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
