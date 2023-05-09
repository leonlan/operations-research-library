class ProblemData:
    def __init__(
        self,
        num_jobs,
        num_machines,
        processing,
        num_factories=0,
        due_dates=None,
        setup=None,
    ):
        self.num_jobs = num_jobs
        self.num_machines = num_machines  # also: stages/units
        self.num_factories = num_factories

        self.processing = processing if processing is not None else []
        self.due_dates = due_dates if due_dates is not None else []
        self.setup = setup if setup is not None else []

    @classmethod
    def from_file(cls, fname, problem_type):
        data = {}

        def read_int_values(fh):
            return [int(x) for x in fh.readline().strip().split()]

        def read_setup(fh, num_machines, num_jobs):
            return [
                [read_int_values(fh) for _ in range(num_jobs)]
                for _ in range(num_machines)
            ]

        with open(fname, "r") as fh:
            data["num_jobs"] = read_int_values(fh)[0]
            data["num_machines"] = read_int_values(fh)[0]

            if problem_type == "Distributedflowshop":
                data["num_factories"] = read_int_values(fh)[0]

            if problem_type == "Tardinessflowshop":
                data["due_dates"] = read_int_values(fh)

            data["processing"] = [
                read_int_values(fh) for _ in range(data["num_jobs"])
            ]

            if problem_type == "Setupflowshop":
                setup = read_setup(fh, data["num_machines"], data["num_jobs"])
                data["setup"] = setup

        return cls(**data)
