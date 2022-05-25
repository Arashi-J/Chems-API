from fastapi import APIRouter, Query, Depends, Body, Path

from app.core.auth import get_current_user, validate_role
from app.crud.crud import create_documents, get_documents
from app.db.database import db
from app.helpers.helpers import db_validation, multiple_db_validation, multiple_populate, populate, set_approval_info, set_update_info
from app.models.chemical import ChemicalCreate, ChemicalRead
from app.models.py_object_id import PyObjectId
from app.models.enums import QueryStatus
from app.models.user import UserRead

chemicals = APIRouter(prefix="/chemicals", tags=["Sustancias Químicas"])

chemicals_collection = db.chemicals
hazards_collection = db.hazards
ppes_collection = db.ppes   

@chemicals.get('/', name="Obtener sustancias químicas", response_model=list[ChemicalRead], status_code=200)
async def get_chemicals(
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

# @chemicals.get('/{id}',name="Obtener sustancia química", response_model=UserRead, status_code=200)
# async def get_chemical(
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

@chemicals.post('/',name="Crear sustancia química", response_model=ChemicalRead, status_code=201)
async def create_chemical(
    chemical: ChemicalCreate = Body(..., title="Datos del la sustancia química", description="Datos de la sustancia química a crear"),
    active_user: UserRead = Depends(get_current_user)
    )->dict:
    """
    Crea una sustancia química. Retorna la sustancia química creada.
    """
    await validate_role(active_user)
    await db_validation(chemical, "chemical", chemicals_collection)
    # await multiple_db_validation(chemical, "hazards", hazards_collection)
    # await multiple_db_validation(chemical, "ppes", ppes_collection)
    chemical = set_update_info(chemical, active_user)
    chemical = set_approval_info(chemical)
    new_chemical = await create_documents(chemical, chemicals_collection)
    # new_user = await populate(new_user, "hazards", hazards_collection)
    # new_user = await populate(new_user, "ppes", ppes_collection)
    return new_chemical

# @chemicals.put('/{id}',name="Actualizar usuario", response_model=UserRead, status_code=202)
# async def update_chemical(
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

@chemicals.put('/approval/{id}', name="Aprobar sustancia química", response_model=ChemicalRead, status_code=202)
async def chemical_approval(
    id: PyObjectId = Path(..., title="ID de la sustancia química", description="El MongoID de la sustancia química a aprobar"),
    active_user: UserRead = Depends(get_current_user)
    
    ):
    #set_approval_info()
    pass