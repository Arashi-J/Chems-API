from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field
from app.models.hazard import Hazard

from app.models.py_object_id import PyObjectId


class ChemicalBase(BaseModel):

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    class Approval(BaseModel):
        approval: bool  | None = None
        approver: str | None = None
        approval_date: datetime  | None = None

    class Phrase(BaseModel):
        code: str
        description: str
    
    chemical: str
    hazards: list[PyObjectId] | None = None
    providers: list[str] | None = None
    manufacturers: list[str] | None = None
    p_phrases: list[Phrase] | None = None
    h_phrases: list[Phrase] | None = None
    ppes: list[PyObjectId] | None = None
    sds: list[str]  | None = None
    fsms: Approval | None = None
    ems: Approval | None = None  
    oshms: Approval | None = None
    status: bool = True
    last_update_by: str | None
    last_update_date: datetime = datetime.now()

class ChemicalCreate(ChemicalBase):
    pass

class ChemicalUpdate(ChemicalBase):
    chemical: str | None = None
    status: bool | None = None

class ChemicalRead(ChemicalBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", title="ID del Usuario", description="MongoID")
    #hazards: list[Hazard]