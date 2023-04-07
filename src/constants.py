from enum import Enum


class ProblemType(Enum):
    FLOWSHOP = "Flowshop"
    NON_FLOWSHOP = "Non-Flowshop"
    HYBRID_FLOWSHOP = "Hybridflowshop"
    DISTRIBUTED_FLOWSHOP = "Distributedflowshop"
    NOWAIT_FLOWSHOP = "Nowaitflowshop"
    SETUP_FLOWSHOP = "Setupflowshop"
    TARDINESS_FLOWSHOP = "Tardinessflowshop"
    JOBSHOP = "Jobshop"
    FLEXIBLE_JOBSHOP = "Flexiblejobshop"
    OPENSHOP = "Openshop"
    PARALLEL_MACHINE = "Parallelmachine"
