from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from typing import Any

from app.models.py_object_id import PyObjectId

class UserBase(BaseModel):
    firstname: str = Field(..., title="Nombre del Usuario", description="Nombre del Usuario.")
    lastname: str  = Field(..., title="Apellido del Usuario", description="Apellido del Usuario.")
    email: EmailStr  = Field(..., title="Correo del Usuario", description="Correo del Usuario.")
    username: str  = Field(..., title="Usuario", description="Se utiliza junto con la contraseña para iniciar sesión.")    
    status: bool = Field(True, title="Estado del Usuario", description="True: Usuario Activo, False: Usuario Inactivo.")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
    
class UserCreate(UserBase):
    password: str = Field(..., title="Contraseña del Usuario", description="Se utiliza junto con el usuario para iniciar sesión")
    areas: list[PyObjectId] = Field([], title="Áreas del Usuario", description="ID de las áreas que puede editar el usuario. MongoID")
    role: PyObjectId | None = Field(None, title="Rol del Usuario", description="Los permisos del usuario se asignan de acuerdo al rol.")
    
class UserUpdate(UserBase):
    firstname: str  | None = Field(None, title="Nombre del Usuario", description="Nombre del Usuario.")
    lastname: str  | None = Field(None, title="Apellido del Usuario", description="Apellido del Usuario.")
    email: EmailStr  | None = Field(None, title="Correo del Usuario", description="Correo del Usuario.")
    username: str  | None = Field(None, title="Usuario", description="Se utiliza para iniciar sesión.")
    password: str | None = Field(None, title="Contraseña del Usuario", description="Se utiliza junto con el usuario para iniciar sesión")
    areas: list[PyObjectId] | None = Field(None, title="Áreas del Usuario", description="ID de las áreas que puede editar el usuario. MongoID")
    role: PyObjectId | None = Field(None, title="Rol del Usuario", description="Los permisos del usuario se asignan de acuerdo al rol.")
    status: bool | None = Field(True, title="Estado del Usuario", description="True: Usuario Activo, False: Usuario Inactivo.")
    
class UserRead(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", title="ID del Usuario", description="MongoID")
    areas: list[dict] = Field(..., title="Áreas del Usuario", description="Áreas que puede editar el usuario.")
    role: Any = Field(..., title="Rol del Usuario", description="Los permisos del usuario se asignan de acuerdo al rol.")

