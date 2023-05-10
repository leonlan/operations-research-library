import os
from typing import List, Optional, Union


class ProblemData:
    def __init__(
        self,
        num_jobs: int,
        num_machines: int,
        processing: List[List[int]],
        num_factories: int = 0,
        due_dates: Optional[List[int]] = None,
        setup: Optional[List[List[int]]] = None,
        machines: Optional[List[List[int]]] = None,
    ):
        self.num_jobs = num_jobs
        self.num_machines = num_machines  # also: stages/units
        self.processing = processing

        self.num_factories = num_factories
        self.due_dates = due_dates or []
        self.setup = setup or []
        self.machines = machines or []  # num machines per stage

    @classmethod
    def from_file(cls, fname: Union[str, os.PathLike], problem_type: str):
        """
        Reads problem data from file.

        Note that the files are benchmark instances from the literature.
        They follow a specific format, which requires the if statements
        to be organized as they are.
        """
        data = {}

        def read_line(fh):
            return [int(x) for x in fh.readline().strip().split()]

        with open(fname, "r") as fh:
            data["num_jobs"] = read_line(fh)[0]
            data["num_machines"] = read_line(fh)[0]

            if problem_type == "Hybridflowshop":
                data["machines"] = read_line(fh)

            if problem_type == "Distributedflowshop":
                data["num_factories"] = read_line(fh)[0]

            if problem_type == "Tardinessflowshop":
                data["due_dates"] = read_line(fh)

            data["processing"] = [
                read_line(fh) for _ in range(data["num_jobs"])
            ]

            if problem_type == "Setupflowshop":
                data["setup"] = [
                    [read_line(fh) for _ in range(data["num_jobs"])]
                    for _ in range(data["num_machines"])
                ]

        return cls(**data)
