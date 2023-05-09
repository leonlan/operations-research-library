from enum import Enum


class ProblemType(Enum):
    FLOWSHOP = "Flowshop"
    DISTRIBUTED_FLOWSHOP = "Distributedflowshop"
    SETUP_FLOWSHOP = "Setupflowshop"
    TARDINESS_FLOWSHOP = "Tardinessflowshop"
    PARALLEL_MACHINE = "Parallelmachine"
    TCT_FLOWSHOP = "TCTflowshop"
