import argparse
from pathlib import Path

from cp import cp
from ProblemData import ProblemData


def parse_instance(loc: str | Path) -> ProblemData:
    with open(loc, "r") as fh:
        lines = fh.readlines()

    nodes = set()
    edges = []

    for line in lines[1:]:
        u, v = [int(node) for node in line.split()]

        nodes.add(u)
        nodes.add(v)
        edges.append((u, v))

    return ProblemData(nodes, edges)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", type=str, default="data/gc_4_1")

    return parser.parse_args()


def main():
    args = parse_args()
    data = parse_instance(Path(args.instance))

    model = cp(data)
    model.solve(LogVerbosity="Terse")


if __name__ == "__main__":
    main()
