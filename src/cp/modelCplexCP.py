from src.cp.Distributedflowshopmodel import Distributedflowshopmodel
from src.cp.flowshopmodel import flowshopmodel
from src.cp.Nowaitflowshopmodel import Nowaitflowshopmodel
from src.cp.parallelmachinemodel import parallelmachinemodel
from src.cp.Setupflowshopmodel import Setupflowshopmodel
from src.cp.Tardinessflowshopmodel import Tardinessflowshopmodel
from src.cp.TCTflowshopmodel import TCTflowshopmodel


###### main ########
def CPmodel_generation(instance, mdl, problemType):
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
