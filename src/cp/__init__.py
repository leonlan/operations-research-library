from .distributed_flow_shop import distributed_flow_shop
from .flow_shop import flow_shop
from .hybrid_flow_shop import hybrid_flow_shop
from .parallel_machines import parallel_machines

CP_MODELS = {
    "flow_shop": flow_shop,
    "tardiness_flow_shop": lambda data: flow_shop(
        data, objective="total_tardiness"
    ),
    "tct_flow_shop": lambda data: flow_shop(
        data, objective="total_completion_times"
    ),
    "setup_flow_shop": lambda data: flow_shop(data, include_setup=True),
    "hybrid_flow_shop": hybrid_flow_shop,
    "unrelated_parallel_machines": parallel_machines,
    "distributed_flow_shop": distributed_flow_shop,
}
