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

        with open(fname, "r") as data:
            data.jobs = int(data.readline().strip().split()[0])
            data.machines = int(data.readline().strip().split()[0])

            if problem_type == "Distributedflowshop":
                data.factories = int(data.readline().strip().split()[0])

            if problem_type == "Tardinessflowshop":
                data.due_dates = [
                    int(x) for x in data.readline().strip().split()
                ]

            data.processing = [
                [int(x) for x in data.readline().strip().split()]
            ]

            for _j in range(data.jobs - 1):
                data.processing.append(
                    [int(x) for x in data.readline().strip().split()]
                )

            if problem_type == "Setupflowshop":
                for i in range(data.machines):
                    data.setup.append([])
                    data.setup[i] = [
                        [int(x) for x in data.readline().strip().split()]
                    ]
                    for _j in range(data.jobs - 1):
                        data.setup[i].append(
                            [int(x) for x in data.readline().strip().split()]
                        )

        return data
