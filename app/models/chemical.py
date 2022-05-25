from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field, validator, AnyUrl

from app.helpers.helpers import drop_duplicates, p_phrase_code_normalizer, h_phrase_code_normalizer, text_normalizer_title
from app.models.approval import Approval
from app.models.hazard import Hazard
from app.models.phrase import Phrase
from app.models.ppe import Ppe
from app.models.py_object_id import PyObjectId

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
    status: bool = True

    _normalize_chemical = validator("chemical", allow_reuse=True)(text_normalizer_title)
    _normalize_p_phrases = validator("p_phrases", allow_reuse=True, each_item=True)(p_phrase_code_normalizer)
    _normalize_h_phrases = validator("h_phrases", allow_reuse=True, each_item=True)(h_phrase_code_normalizer)
    _normalize_hazards = validator("hazards", check_fields=False, allow_reuse=True)(drop_duplicates)
    _normalize_ppes = validator("ppes", check_fields=False, allow_reuse=True)(drop_duplicates)

class ChemicalCreate(ChemicalBase):
    pass

class ChemicalUpdate(ChemicalBase):
    chemical: str | None = None
    status: bool | None = None

class ChemicalRead(ChemicalBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", title="ID del químico", description="MongoID")
    last_update_by: PyObjectId | None
    last_update_date: datetime
    fsms: Approval | None = None
    ems: Approval | None = None  
    oshms: Approval | None = None
    hazards: list[Hazard]
    ppes: list[Ppe]