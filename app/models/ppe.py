from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.py_object_id import PyObjectId

class Ppe(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", title="ID del EPP", description="MongoID")
    ppe: str
    img: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}