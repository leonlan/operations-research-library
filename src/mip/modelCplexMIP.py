from src.mip.Distributedflowshopmodel import Distributedflowshopmodel
from src.mip.flowshopmodel import flowshopmodel
from src.mip.Nowaitflowshopmodel import Nowaitflowshopmodel
from src.mip.parallelmachinemodel import parallelmachinemodel
from src.mip.Setupflowshopmodel import Setupflowshopmodel
from src.mip.Tardinessflowshopmodel import Tardinessflowshopmodel
from src.mip.TCTflowshopmodel import TCTflowshopmodel


###### main ########
def MIPmodel_generation(instance, mdl, problemType):
    if problemType == "Flowshop":
        mdl = flowshopmodel(instance, mdl)
    if problemType == "Distributedflowshop":
        mdl = Distributedflowshopmodel(instance, mdl)
    if problemType == "Nowaitflowshop":
        mdl = Nowaitflowshopmodel(instance, mdl)
    if problemType == "Setupflowshop":
        mdl = Setupflowshopmodel(instance, mdl)
    if problemType == "Tardinessflowshop":
        mdl = Tardinessflowshopmodel(instance, mdl)
    if problemType == "TCTflowshop":
        mdl = TCTflowshopmodel(instance, mdl)
    if problemType == "Parallelmachine":
        mdl = parallelmachinemodel(instance, mdl)
    return mdl
