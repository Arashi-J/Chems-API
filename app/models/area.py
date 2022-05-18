from datetime import datetime

from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.py_object_id import PyObjectId


class Area(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    area: str
    status: bool = True
    chemicals: list[str]
    leader: str | None = None
    last_update_by: str | None
    last_update_date: datetime = datetime.now()


    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
    