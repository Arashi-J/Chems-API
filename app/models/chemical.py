from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field, validator, AnyUrl

from app.helpers.helpers import drop_duplicates, p_phrase_code_normalizer, h_phrase_code_normalizer, text_normalizer_title
from app.models.hazard import Hazard
from app.models.phrase import Phrase
from app.models.ppe import Ppe
from app.models.py_object_id import PyObjectId
from app.models.user import UserBase



class ChemicalBase(BaseModel):

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    chemical: str
    hazards: list[PyObjectId] = []
    providers: list[str] = []
    manufacturers: list[str] = []
    p_phrases: list[Phrase] = []
    h_phrases: list[Phrase] = []
    ppes: list[PyObjectId] = []
    sds: list[AnyUrl] = []


    _normalize_chemical = validator("chemical", allow_reuse=True)(text_normalizer_title)
    _normalize_arrays = validator("providers", "manufacturers", "sds", allow_reuse=True, each_item=True)(text_normalizer_title)
    _normalize_p_phrases = validator("p_phrases", allow_reuse=True, each_item=True)(p_phrase_code_normalizer)
    _normalize_h_phrases = validator("h_phrases", allow_reuse=True, each_item=True)(h_phrase_code_normalizer)
    _remove_duplicates_list_values = validator("hazards", "ppes", "p_phrases", "h_phrases", "sds", "manufacturers", "providers", check_fields=False, allow_reuse=True)(drop_duplicates)

class ChemicalCreate(ChemicalBase):
    pass

class ChemicalUpdate(ChemicalBase):
    chemical: str | None = None
    status: bool | None = None


class Approval(BaseModel):

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


    approval: bool = False
    approbed_by: PyObjectId | None = None
    approval_date: datetime  | None = None

class ApprovalRead(Approval):
    approbed_by: UserBase

class ChemicalRead(ChemicalBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", title="ID del químico", description="MongoID")
    fsms: ApprovalRead | Approval | None = None
    ems: ApprovalRead | Approval | None = None  
    ohsms: ApprovalRead | Approval | None = None
    hazards: list[Hazard]
    ppes: list[Ppe]
    last_update_by: UserBase
    last_update_date: datetime
    status: bool

