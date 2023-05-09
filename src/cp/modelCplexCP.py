from src.cp.Distributedflowshopmodel import Distributedflowshopmodel
from src.cp.flowshopmodel import flowshopmodel
from src.cp.parallelmachinemodel import parallelmachinemodel
from src.cp.Setupflowshopmodel import Setupflowshopmodel
from src.cp.Tardinessflowshopmodel import Tardinessflowshopmodel
from src.cp.TCTflowshopmodel import TCTflowshopmodel


###### main ########
def CPmodel_generation(data, mdl, problemType):
    if problemType == "Flowshop":
        mdl = flowshopmodel(data, mdl)
    if problemType == "Distributedflowshop":
        mdl = Distributedflowshopmodel(data, mdl)
    if problemType == "Setupflowshop":
        mdl = Setupflowshopmodel(data, mdl)
    if problemType == "Tardinessflowshop":
        mdl = Tardinessflowshopmodel(data, mdl)
    if problemType == "TCTflowshop":
        mdl = TCTflowshopmodel(data, mdl)
    if problemType == "Parallelmachine":
        mdl = parallelmachinemodel(data, mdl)
    return mdl
