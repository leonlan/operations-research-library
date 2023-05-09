from src.mip.DistributedFlowShop import DistributedFlowShop
from src.mip.FlowShop import FlowShop
from src.mip.ParallelMachine import ParallelMachine
from src.mip.SetupFlowShop import SetupFlowShop
from src.mip.TardinessFlowShop import TardinessFlowShop
from src.mip.TCTFlowShop import TCTFlowShop


###### main ########
def MIPmodel_generation(data, mdl, problemType):
    if problemType == "Flowshop":
        mdl = FlowShop(data, mdl)
    if problemType == "Distributedflowshop":
        mdl = DistributedFlowShop(data, mdl)
    if problemType == "Setupflowshop":
        mdl = SetupFlowShop(data, mdl)
    if problemType == "Tardinessflowshop":
        mdl = TardinessFlowShop(data, mdl)
    if problemType == "TCTflowshop":
        mdl = TCTFlowShop(data, mdl)
    if problemType == "Parallelmachine":
        mdl = ParallelMachine(data, mdl)
    return mdl
