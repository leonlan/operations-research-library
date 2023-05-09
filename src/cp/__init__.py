from src.cp.Distributedflowshopmodel import Distributedflowshopmodel
from src.cp.flowshopmodel import flowshopmodel
from src.cp.parallelmachinemodel import parallelmachinemodel
from src.cp.Setupflowshopmodel import Setupflowshopmodel
from src.cp.Tardinessflowshopmodel import Tardinessflowshopmodel
from src.cp.TCTflowshopmodel import TCTflowshopmodel

CP_MODELS = {
    "Flowshop": flowshopmodel,
    "Distributedflowshop": Distributedflowshopmodel,
    "Setupflowshop": Setupflowshopmodel,
    "Tardinessflowshop": Tardinessflowshopmodel,
    "TCTflowshop": TCTflowshopmodel,
    "Parallelmachine": parallelmachinemodel,
}
