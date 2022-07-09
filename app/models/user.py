from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, validator
from bson import ObjectId

from app.core.security import hash_password
from app.models.py_object_id import PyObjectId
from app.helpers.helpers import text_normalizer_lower, text_normalizer_title, drop_duplicates
from app.models.role import Role

class UserBase(BaseModel):
    firstname: str = Field(..., title="Nombre del Usuario", description="Nombre del Usuario.")
    lastname: str  = Field(..., title="Apellido del Usuario", description="Apellido del Usuario.")
    email: EmailStr  = Field(..., title="Correo del Usuario", description="Correo del Usuario.")
    username: str  = Field(..., title="Usuario", description="Se utiliza junto con la contraseña para iniciar sesión.")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    _normalize_name = validator("firstname", "lastname", allow_reuse=True)(text_normalizer_title)
    _normalize_username_mail = validator("username", "email", allow_reuse=True)(text_normalizer_lower)
    _remove_duplicates_areas = validator("areas", check_fields=False, allow_reuse=True)(drop_duplicates)
    _hash_password = validator("password", check_fields=False, allow_reuse=True)(hash_password)
   
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
    
class UserRead(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", title="ID del Usuario", description="MongoID")
    areas: list[dict] = Field(..., title="Áreas del Usuario", description="Áreas que puede editar el usuario.")
    role: dict = Field(..., title="Rol del Usuario", description="Los permisos del usuario se asignan de acuerdo al rol.")
    last_update_by: dict
    last_update_date: datetime
    status: bool = Field(..., title="Estado del Usuario", description="True: Usuario Activo, False: Usuario Inactivo.")

class ActiveUser(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id", title="ID del Usuario", description="MongoID")
    role: Role = Field(..., title="Rol del Usuario", description="Los permisos del usuario se asignan de acuerdo al rol.")