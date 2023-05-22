from .ComplexDistributedFlowShop import ComplexDistributedFlowShop
from .DistributedFlowShop import DistributedFlowShop
from .FlowShop import FlowShop
from .HybridFlowShop import HybridFlowShop
from .ParallelMachine import ParallelMachine
from .SetupFlowShop import SetupFlowShop
from .UnrelatedParallelMachines import UnrelatedParallelMachines

CP_MODELS = {
    "Distributedflowshop": DistributedFlowShop,
    "Setupflowshop": SetupFlowShop,
    "Flowshop": FlowShop,
    "Tardinessflowshop": lambda data: FlowShop(
        data, objective="total_tardiness"
    ),
    "TCTflowshop": lambda data: FlowShop(
        data, objective="total_completion_times"
    ),
    "Parallelmachine": ParallelMachine,
    "Hybridflowshop": HybridFlowShop,
    "Unrelatedparallelmachines": UnrelatedParallelMachines,
    "Complexdistributedflowshop": ComplexDistributedFlowShop,
}
