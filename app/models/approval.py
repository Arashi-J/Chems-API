from datetime import datetime

from pydantic import BaseModel
from bson import ObjectId

from app.models.py_object_id import PyObjectId

class Approval(BaseModel):

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


    approval: bool = False
    approbed_by: PyObjectId | None = None
    approval_date: datetime  | None = None