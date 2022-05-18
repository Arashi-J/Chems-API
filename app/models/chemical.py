from datetime import datetime

from pydantic import BaseModel, Field

#from models.py_object_id import PyObjectId
from models.hazard import Hazard
from models.ppe import Ppe
#from models.user import User

class Chemical(BaseModel):

    class Approval(BaseModel):
        approval: bool  | None = None
        approver: str | None = None
        approval_date: datetime  | None = None

    class Phrase(BaseModel):
        code: str
        description: str

    #id: Field(default_factory=PyObjectId, alias="_id")
    chemical: str
    hazards: list[Hazard] | None = None
    providers: list[str] | None = None
    manufacturers: list[str] | None = None
    p_phrases: list[Phrase] | None = None
    h_phrases: list[Phrase] | None = None
    ppes: list[Ppe] | None = None
    sds: list[str]  | None = None
    fsms: Approval
    ems: Approval  
    oshms: Approval
    status: bool = True
    last_update_by: str | None
    last_update_date: datetime = datetime.now()
