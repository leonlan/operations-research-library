class ProblemData:
    def __init__(self):
        self.jobs = 0  # jobs
        self.machines = 0  # machines/stages/units
        self.factories = 0  # factories

        self.processing = []  # processing_times
        self.due_dates = []  # due_dates
        self.setup = []  # setup

    @classmethod
    def from_file(cls, fname, problem_type):
        data = cls()

        with open(fname, "r") as fh:
            data.jobs = int(fh.readline().strip().split()[0])
            data.machines = int(fh.readline().strip().split()[0])

            if problem_type == "Distributedflowshop":
                data.factories = int(fh.readline().strip().split()[0])

            if problem_type == "Tardinessflowshop":
                data.due_dates = [
                    int(x) for x in fh.readline().strip().split()
                ]

            data.processing = [[int(x) for x in fh.readline().strip().split()]]

            for _ in range(data.jobs - 1):
                data.processing.append(
                    [int(x) for x in fh.readline().strip().split()]
                )

            if problem_type == "Setupflowshop":
                for _ in range(data.machines):
                    rows = [
                        [int(x) for x in fh.readline().strip().split()]
                        for _ in range(data.jobs)
                    ]
                    data.setup.append(rows)

        return data
