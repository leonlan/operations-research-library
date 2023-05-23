from enum import Enum


class ProblemType(Enum):
    FLOW_SHOP = "flow_shop"
    DISTRIBUTED_FLOW_SHOP = "Distributedflow_shop"
    SETUP_FLOW_SHOP = "setup_flow_shop"
    TARDINESS_FLOW_SHOP = "tardiness_flow_shop"
    PARALLEL_MACHINE = "parallel_machines"
    TCT_FLOW_SHOP = "tct_flow_shop"
    HYBRID_FLOW_SHOP = "hybrid_flow_shop"
    UNRELATED_PARALLEL_MACHINES = "unrelated_parallel_machines"
    COMPLEX_DISTRIBUTED_FLOW_SHOP = "distributed_flow_shop"
