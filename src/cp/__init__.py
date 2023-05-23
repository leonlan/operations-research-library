from .ComplexDistributedFlowShop import ComplexDistributedFlowShop
from .FlowShop import FlowShop
from .HybridFlowShop import HybridFlowShop

# from .ParallelMachine import ParallelMachine
from .UnrelatedParallelMachines import UnrelatedParallelMachines

CP_MODELS = {
    "Flowshop": FlowShop,
    "Tardinessflowshop": lambda data: FlowShop(
        data, objective="total_tardiness"
    ),
    "TCTflowshop": lambda data: FlowShop(
        data, objective="total_completion_times"
    ),
    "Setupflowshop": lambda data: FlowShop(data, include_setup=True),
    # "Parallelmachine": ParallelMachine,
    "Hybridflowshop": HybridFlowShop,
    "Unrelatedparallelmachines": UnrelatedParallelMachines,
    "Complexdistributedflowshop": ComplexDistributedFlowShop,
}
