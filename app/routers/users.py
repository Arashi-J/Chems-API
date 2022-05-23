from datetime import timedelta
from fastapi import APIRouter, Body, Query, Path, Depends, HTTPException

from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import authenticate_user, create_access_token
from app.core.config import get_settings
from app.crud.crud import get_document_by_id, get_documents, create_documents, update_document
from app.db.database import db
from app.helpers.helpers import populate, multiple_populate, db_validation, multiple_db_validation
from app.models.py_object_id import PyObjectId
from app.models.role import Role
from app.models.token import Token
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
    users = await multiple_populate(users, "role", roles_collection)
    return users

@users.get('/{id}',name="Obtener usuario", response_model=UserRead, status_code=200)
async def get_user(id: PyObjectId = Path(..., title="ID del Usuario", description="El MongoID del usuario a buscar"))->dict:
    """
    Obtiene el usuario correspondiente al ID ingresado.
    """
    await db_validation(None, None, users_collection, False, True, id)
    user = await get_document_by_id(id, users_collection)
    user = await populate(user, "areas", areas_collection, "area")
    user = await populate(user, "role", roles_collection)
    return user

@users.post('/',name="Crear usuario", response_model=UserRead, status_code=201)
async def create_user(user: UserCreate = Body(..., title="Datos del Usuario", description="Datos del usuario a crear"))->dict:
    """
    Crea un usuario. Retorna el usuario Creado.
    """
    await db_validation(user, "username", users_collection)
    await db_validation(user, "email", users_collection)
    await db_validation(user, "role", roles_collection, False, True)
    await multiple_db_validation(user, "areas", areas_collection)
    new_user = await create_documents(user, users_collection)
    new_user = await populate(new_user, "areas", areas_collection, "area")
    new_user = await populate(new_user, "role", roles_collection)
    return new_user

@users.put('/{id}',name="Actualizar usuario", response_model=UserRead, status_code=202)
async def update_user(
    id: PyObjectId =  Path(..., title="ID del Usuario", description="El MongoID del usuario a actualizar"),
    new_data: UserUpdate = Body(..., title="Datos Nuevos", description="Nueva información a actualizar al usuario.")
    )->dict:
    """
    Actualiza los datos del Usuario con el ID ingresado. Retorna el usuario actualizado.
    """
    await db_validation(None, None, users_collection, False, True, id)
    await db_validation(new_data, "username", users_collection)
    await db_validation(new_data, "email", users_collection)
    await db_validation(new_data, "role", roles_collection, False, True)
    await multiple_db_validation(new_data, "areas", areas_collection)
    updated_user = await update_document(id, users_collection, new_data)    
    updated_user = await populate(updated_user, "areas", areas_collection, "area")
    updated_user = await populate(updated_user, "role", roles_collection)
    return updated_user


@users.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm =Depends()):
    user = await authenticate_user(users_collection, form_data.username, form_data.password)
    if not user:
         raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data = {"sub": user["username"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@users.get('/role/{id}',name="Obtener Rol", response_model=Role, status_code=200)
async def get_role(id: PyObjectId = Path(..., title="ID del Rol", description="El MongoID del rol a buscar"))->dict:
    """
    Obtiene el rol correspondiente al ID ingresado.
    """
    await db_validation(None, None, roles_collection, False, True, id)
    role = await get_document_by_id(id, roles_collection)
    return role