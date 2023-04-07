from src.mip.Distributedflowshopmodel import Distributedflowshopmodel
from src.mip.flowshopmodel import flowshopmodel
from src.mip.Nowaitflowshopmodel import Nowaitflowshopmodel
from src.mip.parallelmachinemodel import parallelmachinemodel
from src.mip.Setupflowshopmodel import Setupflowshopmodel
from src.mip.Tardinessflowshopmodel import Tardinessflowshopmodel
from src.mip.TCTflowshopmodel import TCTflowshopmodel


###### main ########
def MIPmodel_generation(data, mdl, problemType):
    if problemType == "Flowshop":
        mdl = flowshopmodel(data, mdl)
    if problemType == "Distributedflowshop":
        mdl = Distributedflowshopmodel(data, mdl)
    if problemType == "Nowaitflowshop":
        mdl = Nowaitflowshopmodel(data, mdl)
    if problemType == "Setupflowshop":
        mdl = Setupflowshopmodel(data, mdl)
    if problemType == "Tardinessflowshop":
        mdl = Tardinessflowshopmodel(data, mdl)
    if problemType == "TCTflowshop":
        mdl = TCTflowshopmodel(data, mdl)
    if problemType == "Parallelmachine":
        mdl = parallelmachinemodel(data, mdl)
    return mdl
