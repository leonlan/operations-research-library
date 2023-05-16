from src.cp.ComplexDistributedFlowShop import ComplexDistributedFlowShop
from src.cp.DistributedFlowShop import DistributedFlowShop
from src.cp.FlowShop import FlowShop
from src.cp.HybridFlowShop import HybridFlowShop
from src.cp.ParallelMachine import ParallelMachine
from src.cp.SetupFlowShop import SetupFlowShop
from src.cp.TardinessFlowShop import TardinessFlowShop
from src.cp.TCTFlowShop import TCTFlowShop
from src.cp.UnrelatedParallelMachines import UnrelatedParallelMachines

CP_MODELS = {
    "Flowshop": FlowShop,
    "Distributedflowshop": DistributedFlowShop,
    "Setupflowshop": SetupFlowShop,
    "Tardinessflowshop": TardinessFlowShop,
    "TCTflowshop": TCTFlowShop,
    "Parallelmachine": ParallelMachine,
    "Hybridflowshop": HybridFlowShop,
    "Unrelatedparallelmachines": UnrelatedParallelMachines,
    "Complexdistributedflowshop": ComplexDistributedFlowShop,
}
