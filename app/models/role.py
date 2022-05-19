from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.py_object_id import PyObjectId

class Role(BaseModel):

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", title="ID del rol", description="MongoID")
    role: str = Field(..., title='Rol', description="Valor único para identificar el rol")
    role_name: str = Field(..., title='Nombre del Rol', description="Nombre completo del Rol")