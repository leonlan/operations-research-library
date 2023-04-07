import time
from pathlib import Path

from Instance import Instance
import modelCplexCP
import modelCplexMIP
import modelGoogleCP
import modelGoogleMIP
import numpy as np
from docplex.cp.model import *
from gurobipy import *
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
            mdl = cplex.Cplex()
            mdl = modelCplexMIP.MIPmodel_generation(instance, mdl, problemType)
            x, y = CPLEX_MIP_solve(
                mdl,
                problemType,
                name,
                time_limit,
                NThreads,
                output,
            )
        if solver == "Gurobi":
            mdl = cplex.Cplex()
            mdl = modelCplexMIP.MIPmodel_generation(instance, mdl, problemType)
            mdl.write("model.lp")
            mdl = gurobipy.read("model.lp")
            x, y = Gurobi_solve(
                mdl,
                problemType,
                name,
                time_limit,
                NThreads,
                output,
            )
        if solver == "Google":
            mdl = pywraplp.Solver.CreateSolver("SCIP")
            mdl = modelGoogleMIP.MIPmodel_generation(
                instance, mdl, problemType
            )
            x, y = Google_MIP_solve(
                mdl,
                problemType,
                name,
                time_limit,
                NThreads,
                output,
            )
        if solver == "Xpress":
            mdl = cplex.Cplex()
            mdl = modelCplexMIP.MIPmodel_generation(instance, mdl, problemType)
            mdl.write("model.lp")
            mdl = xp.problem()
            mdl.read("model", "l")
            x, y = Xpress_MIP_solve(
                mdl,
                problemType,
                name,
                time_limit,
                NThreads,
                output,
            )

    if modelType == "CP":
        if solver == "CPLEX":
            mdl = CpoModel()
            mdl = modelCplexCP.CPmodel_generation(instance, mdl, problemType)
            x, y = CPLEX_CP_solve(
                mdl,
                problemType,
                name,
                time_limit,
                NThreads,
                instance,
                output,
            )
        if solver == "Google":
            mdl = cp_model.CpModel()
            mdl = modelGoogleCP.CPmodel_generation(instance, mdl, problemType)
            x, y = Google_CP_solve(
                mdl,
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
def Xpress_MIP_solve(mdl, problemType, name, time_limit, NThreads, output):
    mdl.controls.outputlog = 0
    mdl.setControl("maxtime", -time_limit)
    mdl.solve()
    if mdl.getProbStatusString() in ["mip_optimal", "mip_solution"]:
        return int(np.round(mdl.attributes.bestbound)), int(
            np.round(mdl.attributes.mipobjval)
        )
    else:
        return "Infeasible", "Unkown"


####### Solve the MIP problem by Google ########
def Google_MIP_solve(mdl, problemType, name, time_limit, NThreads, output):
    mdl.SetTimeLimit(time_limit * 1000)
    status = mdl.Solve()
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        return np.round(mdl.Objective().BestBound()), np.round(
            mdl.Objective().Value()
        )
    else:
        return "Infeasible", "Unkown"


####### Solve the CP problem by Google ########
def Google_CP_solve(mdl, problemType, name, time_limit, NThreads, output):
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(
        mdl
    )  # 0 optimal, 1 feasible, 2 infeasible, 3 unbounded, 4 abnoral, 5 not_solved
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        return np.round(solver.BestObjectiveBound()), np.round(
            solver.ObjectiveValue()
        )
    else:
        return "Infeasible", "Unkown"


####### Solve the MIP problem by Gurobi ########
def Gurobi_solve(mdl, problemType, name, time_limit, NThreads, output):
    mdl.setParam("MIPGapAbs", 0.99999)
    mdl.setParam("MIPGap", 0.0000)
    mdl.setParam("Timelimit", time_limit)
    mdl.setParam("Threads", NThreads)

    mdl.optimize()
    if mdl.status != 1:
        with open(
            "{}\\solution_MIP_Gurobi_{}_{}.txt".format(
                output, problemType, name
            ),
            "w",
        ) as Allc:
            Allc.write(
                "\n MIP Gurobi {} - {} - ({} - {})".format(
                    problemType,
                    name,
                    int(np.round(mdl.objbound)),
                    int(np.round(mdl.objVal)),
                )
            )
            for v in mdl.getVars():
                if v.x != 0:
                    if v.varName.startswith("C"):
                        Allc.write("\n")
                        Allc.write(v.varName)
                        Allc.write(" ")
                        Allc.write(str(np.round(v.x)))
        return int(np.round(mdl.objbound)), int(np.round(mdl.objVal))
    else:
        return "Infeasible", "Unkown"


####### Solve the MIP problem by CPLEX ########
def CPLEX_MIP_solve(mdl, problemType, name, time_limit, NThreads, output):
    mdl.parameters.timelimit.set(time_limit)
    mdl.parameters.mip.tolerances.absmipgap.set(0.99999)
    mdl.parameters.mip.tolerances.mipgap.set(0.00000)
    mdl.parameters.threads.set(NThreads)
    mdl.set_log_stream(None)
    mdl.set_error_stream(None)
    mdl.set_warning_stream(None)
    mdl.set_results_stream(None)
    # mdl.write('..\\LPs\\{}\\model_{}_{}.lp'.format(problemType,problemType,name))
    # comment to generate only LP files
    # mdl.write('model.lp')
    # mdl.parameters.tune_problem_set(filenames=["model.lp"])
    mdl.solve()
    if (
        mdl.solution.get_status_string(status_code=None)
        != "integer infeasible"
        and mdl.solution.get_status_string(status_code=None)
        != "time limit exceeded, no integer solution"
    ):
        with open(
            "{}\\solution_MIP_CPLEX_{}_{}.txt".format(
                output, problemType, name
            ),
            "w",
        ) as Allc:
            Allc.write(
                "\n MIP CPLEX {} - {} - ({} - {})".format(
                    problemType,
                    name,
                    int(np.round(mdl.solution.MIP.get_best_objective())),
                    int(np.round(mdl.solution.get_objective_value())),
                )
            )
            for i, x in enumerate(mdl.solution.get_values()):
                if x != 0:
                    if mdl.variables.get_names(i).startswith("C"):
                        Allc.write("\n")
                        Allc.write(mdl.variables.get_names(i))
                        Allc.write(" ")
                        Allc.write(str(np.round(x)))
        return int(np.round(mdl.solution.MIP.get_best_objective())), int(
            np.round(mdl.solution.get_objective_value())
        )
    else:
        return "Infeasible", "Unkown"
    # end comment


####### Solve the CP problem by DOCPLEX ########
def CPLEX_CP_solve(
    mdl, problemType, name, time_limit, NThreads, instance, output
):
    msol = mdl.solve(
        TimeLimit=time_limit,
        Workers=NThreads,
        LogVerbosity="Quiet",
        WarningLevel=0,
        OptimalityTolerance=0.99,
        RelativeOptimalityTolerance=0.0,
    )

    if msol.solution.is_empty() is False:
        fname = "solution_CP_CPLEX_{}_{}.txt".format(problemType, name)
        with open(Path(output) / fname, "w") as Allc:
            Allc.write(
                "\n CP {} - {} - ({} - {})".format(
                    problemType,
                    name,
                    int(np.round(msol.get_objective_bounds()[0])),
                    int(np.round(msol.get_objective_values()[0])),
                )
            )
            if problemType != "Parallelmachine":
                for j in range(instance.n):
                    Allc.write("\n")
                    q = instance.g
                    if problemType != "Parallelmachine":
                        for i in range(q):
                            var = msol.get_var_solution("T_{}_{}".format(j, i))
                            x = var.get_end()
                            y = var.get_start()
                            var.get_value()
                            Allc.write(str(y))
                            Allc.write(" ")
                            Allc.write(str(x))
                            Allc.write("\t")
                    else:
                        for i in range(q):
                            var = msol.get_var_solution("A_{}_{}".format(j, i))
                            x = var.get_end()
                            y = var.get_start()
                            var.get_value()
                            Allc.write(str(y))
                            Allc.write(" ")
                            Allc.write(str(x))
                            Allc.write("\t")

        return int(np.round(msol.get_objective_bounds()[0])), int(
            np.round(msol.get_objective_values()[0])
        )
    else:
        return "Infeasible", "Unkown"
