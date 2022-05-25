from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.py_object_id import PyObjectId

class Hazard(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", title="ID del peligro", description="MongoID")
    code: str
    hazard: str
    description: str
    precaution: str
    pictogram: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}