import os
from typing import List, Optional, Union

import numpy as np
import numpy.random as rnd

rnd.seed(42)


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
        self.machines = (
            machines if machines is not None else range(num_machines)
        )
        self.eligible = eligible if eligible is not None else []

        self.num_stages = num_stages

        # Additional useful problem data
        self.num_lines = self.num_factories
        self.num_units = self.num_machines

        self.jobs = list(range(self.num_jobs))
        self.stages = list(range(self.num_stages))
        self.lines = list(range(self.num_lines))
        self.units = list(range(self.num_machines))

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

            if problem_type == "hybrid_flow_shop":
                data["machines"] = read_line(fh)
                data["num_stages"] = data["num_machines"]

            if "distributed_flow_shop" in problem_type.lower():
                data["num_factories"] = read_line(fh)[0]

            if problem_type == "tardiness_flow_shop":
                data["due_dates"] = read_line(fh)

            data["processing"] = [
                read_line(fh) for _ in range(data["num_jobs"])
            ]

            if problem_type in [
                "setup_flow_shop",
                "unrelated_parallel_machines",
            ]:
                data["setup"] = [
                    [read_line(fh) for _ in range(data["num_jobs"])]
                    for _ in range(data["num_machines"])
                ]

            if problem_type == "unrelated_parallel_machines":
                data["eligible"] = (
                    np.ones_like(data["processing"]).astype(int).tolist()
                )

            if problem_type == "hybrid_flow_shop":
                # HACK to add setup and eligibility data to hybrid flow_shop
                n_jobs, n_stages, n_machines = (
                    data["num_jobs"],
                    data["num_stages"],
                    data["num_machines"],
                )

                shape_eligible = (n_jobs, n_stages, n_machines)
                data["eligible"] = np.ones(shape_eligible).astype(int).tolist()

                shape_setup = (n_jobs, n_jobs, n_stages, n_machines)
                data["setup"] = np.ones(shape_setup).astype(int)

            if problem_type == "distributed_flow_shop":
                # HACK Adding unrelated machines, setup and eligibility data
                # to complex distributed flow shop.
                num_jobs = data["num_jobs"]
                num_machines = data["num_machines"]
                num_factories = data["num_factories"]

                # Repeat the processing times for each identical machine for
                # each factory and add some noise.
                proc = np.array(data["processing"])
                proc = np.repeat(proc[:, :, np.newaxis], num_factories, axis=2)
                noise = rnd.randint(1, 10, size=proc.shape)
                data["processing"] = proc + noise

                # Setup times: very high setup times between two jobs that
                # are of the same parity. This ensures that the schedules will
                # always schedule odd jobs together, and even jobs together.
                shape = (num_jobs, num_jobs, num_machines, num_factories)
                setup = np.ones(shape, dtype=int) * 100
                setup[::2, ::2, :, :] = 0
                setup[1::2, 1::2, :, :] = 0
                data["setup"] = setup

                # Line eligibility: jobs are not eligible on every production
                # line. Even numbered jobs are not allowed on the first line,
                # odd numbered jobs are not allowed on the second line.
                eligible_shape = (num_jobs, num_machines, num_factories)
                eligible = np.ones(eligible_shape, dtype=bool)
                eligible[::2, :, 0] = False
                eligible[1::2, :, 1] = False
                data["eligible"] = eligible

        return cls(**data)
