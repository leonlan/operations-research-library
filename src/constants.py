from enum import Enum


class ProblemType(Enum):
    FLOW_SHOP = "Flowshop"
    DISTRIBUTED_FLOW_SHOP = "Distributedflowshop"
    SETUP_FLOW_SHOP = "Setupflowshop"
    TARDINESS_FLOW_SHOP = "Tardinessflowshop"
    PARALLEL_MACHINE = "Parallelmachine"
    TCT_FLOW_SHOP = "TCTflowshop"
    HYBRID_FLOW_SHOP = "Hybridflowshop"
