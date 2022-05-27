from fastapi import APIRouter, Body, Query, Path, Depends

from app.core.auth import get_current_user, login_for_access_token, validate_role
from app.crud.crud import delete_document, get_document_by_id, get_documents, create_document, update_document
from app.db.database import db
from app.helpers.helpers import populate, multiple_populate, db_validation, multiple_db_validation, set_status, set_update_info
from app.models.py_object_id import PyObjectId
from app.models.role import Role
from app.models.token import Token
from app.models.user import UserRead, UserCreate, UserUpdate
from app.models.enums import QueryStatus

users = APIRouter(prefix='/users', tags=['Usuarios'])

users_collection = db.users
areas_collection = db.areas
roles_collection = db.roles

@users.get('/', name="Obtener usuarios", response_model=list[UserRead], status_code=200)
async def get_users(
    skip: int = Query(0, title="Salto de página", description="Índica desde el cual número de documento inicia la consulta a la base de datos"),
    limit: int | None = Query(None, title="Límite", description="Índica la cantidad máxima que obtendrá la consulta a la Base de Datos"),
    status: QueryStatus = Query(QueryStatus.all, title="Estado", description="Determina si se requiere que la consulta obtenga los usuarios activos, inactivos o todos"),
    active_user = Depends(get_current_user)
    )->list:
    """
    Obtiene todos los usuarios en la base de datos.
    """
    await validate_role(active_user)
    users = await get_documents(users_collection, skip, limit, status)
    users = await multiple_populate(users, "areas", areas_collection, "area")
    users = await multiple_populate(users, "role", roles_collection)
    users = await multiple_populate(users, "last_update_by", users_collection, "username")
    return users

@users.get('/{id}',name="Obtener usuario", response_model=UserRead, status_code=200)
async def get_user(
    id: PyObjectId = Path(..., title="ID del Usuario", description="El MongoID del usuario a buscar"),
    active_user = Depends(get_current_user)
    )->dict:
    """
    Obtiene el usuario correspondiente al ID ingresado.
    """
    await validate_role(active_user)
    await db_validation(collection=users_collection, check_duplicate=False, search_id=True, query_value=id)
    user = await get_document_by_id(id, users_collection)
    user = await populate(user, "areas", areas_collection, "area")
    user = await populate(user, "role", roles_collection)
    user = await populate(user, "last_update_by", users_collection, "username")
    return user

@users.post('/',name="Crear usuario", response_model=UserRead, status_code=201)
async def create_user(
    user: UserCreate = Body(..., title="Datos del Usuario", description="Datos del usuario a crear"),
    active_user = Depends(get_current_user)
    )->dict:
    """
    Crea un usuario. Retorna el usuario Creado.
    """
    await validate_role(active_user)
    await db_validation(data_in=user, field_to_validate="username", collection=users_collection)
    await db_validation(data_in=user, field_to_validate="email", collection=users_collection)
    await db_validation(data_in=user, field_to_validate="role", collection=roles_collection, check_duplicate=False, search_id=True)
    await multiple_db_validation(data_in=user, field_to_validate="areas", collection=areas_collection)
    user = set_status(user)
    user = set_update_info(user, active_user)
    new_user = await create_document(user, users_collection)
    new_user = await populate(new_user, "areas", areas_collection, "area")
    new_user = await populate(new_user, "role", roles_collection)
    new_user = await populate(new_user, "last_update_by", users_collection, "username")
    return new_user

@users.put('/{id}',name="Actualizar usuario", response_model=UserRead, status_code=202)
async def update_user(
    id: PyObjectId =  Path(..., title="ID del Usuario", description="El MongoID del usuario a actualizar"),
    new_data: UserUpdate = Body(..., title="Datos Nuevos", description="Nueva información a actualizar al usuario."),
    active_user = Depends(get_current_user)
    )->dict:
    """
    Actualiza los datos del Usuario con el ID ingresado. Retorna el usuario actualizado.
    """
    await validate_role(active_user)
    await db_validation(collection=users_collection, check_duplicate=False, search_id=True, query_value=id)
    await db_validation(data_in=new_data, field_to_validate="username", collection=users_collection)
    await db_validation(data_in=new_data, field_to_validate="email", collection=users_collection)
    await db_validation(data_in=new_data, field_to_validate="role", collection=roles_collection, check_duplicate=False, search_id=True)
    await multiple_db_validation(data_in=new_data, field_to_validate="areas", collection=areas_collection)
    updated_user = await update_document(id, users_collection, new_data)    
    updated_user = await populate(updated_user, "areas", areas_collection, "area")
    updated_user = await populate(updated_user, "role", roles_collection)
    updated_user = await populate(updated_user, "last_update_by", users_collection, "username")
    return updated_user


@users.delete("({id}", name="Eliminar usuario", response_model=UserRead, status_code=200)
async def delete_user(id: PyObjectId, active_user = Depends(get_current_user))->dict:
    """
    Cambia el usuario correspondiente al ID ingresado a inactivo (False).
    """
    await validate_role(active_user)
    await db_validation(collection=users_collection, check_duplicate=False , search_id=True, query_value=id)
    deleted_user = await delete_document(id, users_collection)
    deleted_user = await populate(deleted_user, "areas", areas_collection, "area")
    deleted_user = await populate(deleted_user, "role", roles_collection)
    deleted_user = await populate(deleted_user, "last_update_by", users_collection, "username")
    return deleted_user

@users.post("/login", response_model=Token)
async def login(token: Token = Depends(login_for_access_token)):
    return token
    
@users.get('/roles/', name="Obtener Roles", response_model=list[Role], status_code=200)
async def get_roles(active_user = Depends(get_current_user))->list:
    """
    Obtiene todos los roles en la base de datos.
    """
    await validate_role(active_user)
    roles = await get_documents(roles_collection)
    return roles

@users.get('/roles/{id}', name="Obtener rol", response_model=Role, status_code=200)
async def get_user(
    id: PyObjectId = Path(..., title="ID del rol", description="El MongoID del rol a buscar"),
    active_user = Depends(get_current_user)
    )->dict:
    """
    Obtiene el usuario correspondiente al ID ingresado.
    """
    await validate_role(active_user)
    await db_validation(collection=roles_collection, check_duplicate=False, search_id=True, query_value=id)
    role = await get_document_by_id(id, roles_collection)
    return role

