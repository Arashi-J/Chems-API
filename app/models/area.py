from datetime import datetime

from pydantic import BaseModel, Field, validator
from bson import ObjectId
from app.helpers.helpers import drop_duplicates, text_normalizer_title

from app.models.py_object_id import PyObjectId


class AreaBase(BaseModel):
    area: str
    status: bool = True
    chemicals: list[PyObjectId] = []
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    _normalize_area = validator("area", allow_reuse=True)(text_normalizer_title)
    _remove_duplicates_chemicals = validator("chemicals", check_fields=False, allow_reuse=True)(drop_duplicates)

class AreaCreate(AreaBase):
    pass

class AreaUpdate(AreaBase):
    area: str | None = None
    status: bool | None = None

class AreaRead(AreaBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", title="ID del químico", description="MongoID")
    last_update_by: dict | None
    last_update_date: datetime
    chemicals: list[dict]

