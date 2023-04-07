class ProblemData:
    def __init__(self):
        self.n = 0  # jobs
        self.g = 0  # stages
        self.f = 0  # factories

        # TODO rename these indices
        self.o = []  # operations
        self.p = []  # processing_times
        self.r = []  # routes
        self.m = []  # machine
        self.d = []  # duedates
        self.s = []  # setup

    @classmethod
    def from_file(cls, fname, problem_type):
        data = cls()

        with open(fname, "r") as data:
            data.n = int(data.readline().strip().split()[0])
            data.g = int(data.readline().strip().split()[0])

            if problem_type == "Distributedflowshop":
                data.f = int(data.readline().strip().split()[0])

            if problem_type == "Tardinessflowshop":
                data.d = [int(x) for x in data.readline().strip().split()]

            data.p = [[int(x) for x in data.readline().strip().split()]]
            for _j in range(data.n - 1):
                data.p.append(
                    [int(x) for x in data.readline().strip().split()]
                )

            if problem_type == "Setupflowshop":
                for i in range(data.g):
                    data.s.append([])
                    data.s[i] = [
                        [int(x) for x in data.readline().strip().split()]
                    ]
                    for _j in range(data.n - 1):
                        data.s[i].append(
                            [int(x) for x in data.readline().strip().split()]
                        )

        return data
