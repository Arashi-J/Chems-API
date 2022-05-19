from turtle import title
from fastapi import APIRouter, Body, Query, Path

from app.db.database import db

from app.crud.crud import get_document_by_id, get_documents, create_documents, update_document
from app.helpers.helpers import populate, multiple_populate, db_validation, multiple_db_validation
from app.models.py_object_id import PyObjectId
from app.models.role import Role
from app.models.user import UserRead, UserCreate, UserUpdate
from app.models.query_status import QueryStatus

users = APIRouter(prefix='/users', tags=['Usuarios'])

users_collection = db.users
areas_collection = db.areas
roles_collection = db.roles

@users.get('/', name="Obtener usuarios", response_model=list[UserRead], status_code=200)
async def get_users(
    skip: int = Query(0, title="Salto de página", description="Índica desde el cual número de documento inicia la consulta a la base de datos"),
    limit: int = Query(10, title="Límite", description="Índica la cantidad máxima que obtendrá la consulta a la Base de Datos"),
    status: QueryStatus = Query(QueryStatus.all, title="Estado", description="Determina si se requiere que la consulta obtenga los usuarios activos, inactivos o todos")
    )->list:
    """
    Obtiene todos los usuarios de a base de datos.
    """
    users = await get_documents(users_collection, skip, limit, status)
    users = await multiple_populate(users, "areas", areas_collection, "area")
    users = await multiple_populate(users, "role", roles_collection, "role_name")
    return users

@users.get('/{id}',name="Obtener usuario", response_model=UserRead, status_code=200)
async def get_user(id: PyObjectId = Path(..., title="ID del Usuario", description="El MongoID del usuario a buscar"))->dict:
    """
    Obtiene el usuario correspondiente al ID ingresado.
    """
    user = await get_document_by_id(id, users_collection)
    user = await populate(user, "areas", areas_collection, "area")
    user = await populate(user, "role", roles_collection, "role_name")
    return user

@users.post('/',name="Crear usuario", response_model=UserRead, status_code=201)
async def create_user(user: UserCreate = Body(..., title="Datos del Usuario", description="Datos del usuario a crear"))->dict:
    """
    Crea un usuario. Retorna el usuario Creado.
    """
    await db_validation(user, "username", users_collection)
    await db_validation(user, "email", users_collection)
    await db_validation(user, "role", roles_collection, False, True)
    new_user = await create_documents(user, users_collection)
    new_user = await populate(new_user, "areas", areas_collection, "area")
    new_user = await populate(new_user, "role", roles_collection, "role")
    return new_user

@users.put('/{id}',name="Actualizar usuario", response_model=UserRead, status_code=202)
async def update_user(
    id: PyObjectId =  Path(..., title="ID del Usuario", description="El MongoID del usuario a actualizar"),
    new_data: UserUpdate = Body(..., title="Datos Nuevos", description="Nueva información a actualizar al usuario.")
    )->dict:
    """
    Actualiza los datos del Usuario con el ID ingresado. Retorna el usuario actualizado.
    """
    await db_validation(new_data, "username", users_collection, True)
    await db_validation(new_data, "email", users_collection, True)
    updated_user = await update_document(id, users_collection, new_data)    
    updated_user = await populate(updated_user, "areas", areas_collection, "area")
    return updated_user


@users.get('/role/{id}',name="Obtener Rol", response_model=Role, status_code=200)
async def get_role(id: PyObjectId = Path(..., title="ID del Rol", description="El MongoID del rol a buscar"))->dict:
    """
    Obtiene el rol correspondiente al ID ingresado.
    """
    role = await get_document_by_id(id, roles_collection)
    return role