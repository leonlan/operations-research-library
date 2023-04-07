# python src/main.py Flexiblejobshop CP 3600 1 20 CPLEX 4 data/Flexiblejobshop/New/ tmp

import sys
import argparse

import models

parser = argparse.ArgumentParser(description="Run a benchmark.")
parser.add_argument(
    "problem_name",
    type=str,
    default="Parallelmachine",
    nargs="?",
    help="Name of the problem instance.",
)
parser.add_argument(
    "modelType",
    type=str,
    default="CP",
    nargs="?",
    help="Type of model to use (CP or LP).",
)
parser.add_argument(
    "computational_time",
    type=int,
    default=10,
    nargs="?",
    help="Maximum computational time in seconds.",
)
parser.add_argument(
    "First",
    type=int,
    default=151,
    nargs="?",
    help="Index of the first benchmark instance.",
)
parser.add_argument(
    "Last",
    type=int,
    default=151,
    nargs="?",
    help="Index of the last benchmark instance.",
)
parser.add_argument(
    "Solver",
    type=str,
    default="Google",
    help="Solver to use (CPLEX or Google).",
)
parser.add_argument(
    "NThreads", type=int, default=4, help="Number of threads to use."
)
parser.add_argument(
    "address", type=str, help="Path to the problem instance files."
)
parser.add_argument("output", type=str, help="Path to the output folder.")

args = parser.parse_args()

for benchmark in range(args.First, args.Last + 1):
    if args.modelType == "CP":
        if args.Solver not in ["CPLEX", "Google"]:
            continue
        if (
            args.Solver == "Google"
            and args.modelType == "CP"
            and args.problem_name
            not in [
                "Non-Flowshop",
                "Hybridflowshop",
                "Nowaitflowshop",
                "Jobshop",
                "Flexiblejobshop",
                "Openshop",
                "Parallelmachine",
            ]
        ):
            continue
    try:
        n, g, Time, LB, UB, GAP = models.main(
            args.computational_time,
            benchmark,
            args.problem_name,
            args.modelType,
            args.Solver,
            args.NThreads,
            args.address,
            args.output,
        )
        result = open(
            "{}/result_{}_{}_{}_{}_{}.txt".format(
                args.output,
                args.modelType,
                args.problem_name,
                args.computational_time,
                args.NThreads,
                benchmark,
            ),
            "a",
        )
        result.write(
            "\n{}\t {}\t {}\t {}\t {}\t {}\t {}\t {}\t {}\t {}".format(
                args.problem_name,
                args.Solver,
                args.modelType,
                benchmark,
                n,
                g,
                LB,
                UB,
                GAP,
                Time,
            )
        )
        result.close()
    except:
        result = open(
            "{}/result_{}_{}_{}_{}_{}.txt".format(
                args.output,
                args.modelType,
                args.problem_name,
                args.computational_time,
                args.NThreads,
                benchmark,
            ),
            "a",
        )
        result.write(
            "\n{}\t {}\t {}\t {}\t {} \t {}".format(
                args.problem_name,
                args.Solver,
                args.modelType,
                benchmark,
                sys.exc_info()[0],
                sys.exc_info()[1],
            )
        )
        result.close()
        print("Error:", sys.exc_info()[0], sys.exc_info()[1])

print("\n\nDone")
