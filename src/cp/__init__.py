from .distributed_flow_shop import distributed_flow_shop
from .flow_shop import flow_shop
from .hybrid_flow_shop import hybrid_flow_shop
from .parallel_machines import parallel_machines

CP_MODELS = {
    "Flowshop": flow_shop,
    "Tardinessflowshop": lambda data: flow_shop(
        data, objective="total_tardiness"
    ),
    "TCTflowshop": lambda data: flow_shop(
        data, objective="total_completion_times"
    ),
    "Setupflowshop": lambda data: flow_shop(data, include_setup=True),
    "Hybridflowshop": hybrid_flow_shop,
    "Unrelatedparallelmachines": parallel_machines,
    "Complexdistributedflowshop": distributed_flow_shop,
}
