from fastapi import APIRouter, Query, Depends

from app.core.auth import get_current_user, validate_role
from app.crud.crud import get_documents
from app.db.database import db
from app.helpers.helpers import multiple_populate
from app.models.chemical import ChemicalRead
from app.models.py_object_id import PyObjectId
from app.models.query_status import QueryStatus
from app.models.user import UserRead

chemicals = APIRouter(prefix="/chemicals", tags=["Químicos"])

chemicals_collection = db.chemicals
hazards_collection = db.hazards
ppes_collection = db.ppes

@chemicals.get('/', name="Obtener áreas", response_model=list[ChemicalRead], status_code=200)
async def get_users(
    skip: int = Query(0, title="Salto de página", description="Índica desde el cual número de documento inicia la consulta a la base de datos"),
    limit: int = Query(10, title="Límite", description="Índica la cantidad máxima que obtendrá la consulta a la Base de Datos"),
    status: QueryStatus = Query(QueryStatus.all, title="Estado", description="Determina si se requiere que la consulta obtenga los químicos activos, inactivos o todos"),
    active_user: UserRead = Depends(get_current_user)
    )->list:
    """
    Obtiene todos las áreas en la base de datos.
    """
    await validate_role(active_user)
    areas = await get_documents(chemicals_collection, skip, limit, status)
    areas = await multiple_populate(areas, "hazards", hazards_collection, "hazard")
    areas = await multiple_populate(areas, "ppes", ppes_collection, "ppe")
    return areas

# @chemicals.get('/{id}',name="Obtener usuario", response_model=UserRead, status_code=200)
# async def get_user(
#     id: PyObjectId = Path(..., title="ID del Usuario", description="El MongoID del usuario a buscar"),
#     active_user: UserRead = Depends(get_current_user)
#     )->dict:
#     """
#     Obtiene el usuario correspondiente al ID ingresado.
#     """
#     await validate_role(active_user)
#     await db_validation(None, None, users_collection, False, True, id)
#     user = await get_document_by_id(id, users_collection)
#     user = await populate(user, "areas", areas_collection, "area")
#     user = await populate(user, "role", roles_collection)
#     return user

# @chemicals.post('/',name="Crear usuario", response_model=UserRead, status_code=201)
# async def create_user(
#     user: UserCreate = Body(..., title="Datos del Usuario", description="Datos del usuario a crear"),
#     active_user: UserRead = Depends(get_current_user)
#     )->dict:
#     """
#     Crea un usuario. Retorna el usuario Creado.
#     """
#     await validate_role(active_user)
#     await db_validation(user, "username", users_collection)
#     await db_validation(user, "email", users_collection)
#     await db_validation(user, "role", roles_collection, False, True)
#     await multiple_db_validation(user, "areas", areas_collection)
#     new_user = await create_documents(user, users_collection)
#     new_user = await populate(new_user, "areas", areas_collection, "area")
#     new_user = await populate(new_user, "role", roles_collection)
#     return new_user

# @chemicals.put('/{id}',name="Actualizar usuario", response_model=UserRead, status_code=202)
# async def update_user(
#     id: PyObjectId =  Path(..., title="ID del Usuario", description="El MongoID del usuario a actualizar"),
#     new_data: UserUpdate = Body(..., title="Datos Nuevos", description="Nueva información a actualizar al usuario."),
#     active_user: UserRead = Depends(get_current_user)
#     )->dict:
#     """
#     Actualiza los datos del Usuario con el ID ingresado. Retorna el usuario actualizado.
#     """
#     await validate_role(active_user)
#     await db_validation(None, None, users_collection, False, True, id)
#     await db_validation(new_data, "username", users_collection)
#     await db_validation(new_data, "email", users_collection)
#     await db_validation(new_data, "role", roles_collection, False, True)
#     await multiple_db_validation(new_data, "areas", areas_collection)
#     updated_user = await update_document(id, users_collection, new_data)    
#     updated_user = await populate(updated_user, "areas", areas_collection, "area")
#     updated_user = await populate(updated_user, "role", roles_collection)
#     return updated_user