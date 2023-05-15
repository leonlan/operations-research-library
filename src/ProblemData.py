import os
from typing import List, Optional, Union

import numpy as np


class ProblemData:
    def __init__(
        self,
        num_jobs: int,
        num_machines: int,
        processing: List[List[int]],
        num_factories: int = 0,
        num_stages: int = 0,
        due_dates: Optional[List[int]] = None,
        setup: Optional[List[List[int]]] = None,
        machines: Optional[List[List[int]]] = None,
        eligible: Optional[List[List[int]]] = None,
    ):
        self.num_jobs = num_jobs
        self.num_machines = num_machines  # also: stages/units
        self.processing = processing

        self.num_factories = num_factories
        self.due_dates = due_dates if due_dates is not None else []
        self.setup = setup if setup is not None else []
        # num machines per stage
        self.machines = machines if machines is not None else []
        self.eligible = eligible if eligible is not None else []

        self.num_stages = num_stages

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
                data["num_stages"] = data["num_machines"]

            if problem_type == "Distributedflowshop":
                data["num_factories"] = read_line(fh)[0]

            if problem_type == "Tardinessflowshop":
                data["due_dates"] = read_line(fh)

            data["processing"] = [
                read_line(fh) for _ in range(data["num_jobs"])
            ]

            if problem_type in ["Setupflowshop", "Unrelatedparallelmachines"]:
                data["setup"] = [
                    [read_line(fh) for _ in range(data["num_jobs"])]
                    for _ in range(data["num_machines"])
                ]

            if problem_type == "Unrelatedparallelmachines":
                data["eligible"] = (
                    np.ones_like(data["processing"]).astype(int).tolist()
                )

            if problem_type == "Hybridflowshop":
                # HACK to add setup and eligibility data to hybrid flowshop
                n_jobs, n_stages, n_machines = (
                    data["num_jobs"],
                    data["num_stages"],
                    data["num_machines"],
                )

                shape_eligible = (n_jobs, n_stages, n_machines)
                data["eligible"] = np.ones(shape_eligible).astype(int).tolist()

                shape_setup = (n_jobs, n_jobs, n_stages, n_machines)
                data["setup"] = np.ones(shape_setup).astype(int)

        return cls(**data)
