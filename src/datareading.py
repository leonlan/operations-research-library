#### Structure for instance data #######
class Instance:
    def __init__(self):
        self.n = 0  # jobs
        self.g = 0  # stages
        self.f = 0  # factories

        self.o = []  # operations
        self.p = []  # processing_times
        self.r = []  # routes
        self.m = []  # machine
        self.d = []  # duedates
        self.s = []  # setup


####### data entry ########
def dataentry(filename, problemType):
    instance = Instance()
    with open(filename, "r") as data:
        instance.n = int(data.readline().strip().split()[0])
        instance.g = int(data.readline().strip().split()[0])

        if problemType == "Distributedflowshop":
            instance.f = int(data.readline().strip().split()[0])

        if problemType == "Tardinessflowshop":
            instance.d = [int(x) for x in data.readline().strip().split()]

        instance.p = [[int(x) for x in data.readline().strip().split()]]
        for _j in range(instance.n - 1):
            instance.p.append(
                [int(x) for x in data.readline().strip().split()]
            )

        if problemType == "Setupflowshop":
            for i in range(instance.g):
                instance.s.append([])
                instance.s[i] = [
                    [int(x) for x in data.readline().strip().split()]
                ]
                for _j in range(instance.n - 1):
                    instance.s[i].append(
                        [int(x) for x in data.readline().strip().split()]
                    )

    return instance
