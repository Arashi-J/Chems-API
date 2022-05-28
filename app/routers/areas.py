from fastapi import APIRouter, Depends, Query, Path, Body

from app.core.auth import get_current_user, validate_area_auth, validate_role
from app.crud.crud import create_document, delete_restore_document, get_document_by_id, get_documents, update_document
from app.db.database import db
from app.helpers.helpers import db_validation, drop_inactive_nested_ids, multiple_db_validation, multiple_populate, populate, set_status, set_update_info
from app.models.area import AreaCreate, AreaRead, AreaUpdate
from app.models.enums import QueryStatus
from app.models.py_object_id import PyObjectId

areas = APIRouter(prefix="/areas", tags=["Áreas"])

areas_collection = db.areas
chemicals_collection = db.chemicals
users_collection = db.users

@areas.get('/', name="Obtener áreas", response_model=list[AreaRead], status_code=200, dependencies=[Depends(get_current_user)])
async def get_areas(
    skip: int = Query(0, title="Salto de página", description="Índica desde el cual número de documento inicia la consulta a la base de datos"),
    limit: int | None = Query(None, title="Límite", description="Índica la cantidad máxima que obtendrá la consulta a la Base de Datos"),
    status: QueryStatus = Query(QueryStatus.all, title="Estado", description="Determina si se requiere que la consulta obtenga las áreas activas, inactivas o todas"),
    )->list:
    """
    Obtiene todas las áreas en la base de datos.
    """
    areas = await get_documents(areas_collection, skip, limit, status)
    areas = await multiple_populate(areas, "chemicals", chemicals_collection, "chemical")
    areas = await multiple_populate(areas, "last_update_by", users_collection, "username")

    return areas

@areas.get('/{id}',name="Obtener áreas", response_model=AreaRead, status_code=200, dependencies=[Depends(get_current_user)])
async def get_chemical(
    id: PyObjectId = Path(..., title="ID del área", description="El MongoID del área a buscar"),
    )->dict:
    """
    Obtiene área correspondiente al ID ingresado.
    """
    await db_validation(collection=areas_collection, check_duplicate=False, search_id=True, query_value=id)
    area = await get_document_by_id(id, areas_collection)
    area = await populate(area, "chemicals", chemicals_collection, "chemical")
    area = await populate(area, "last_update_by", users_collection, "username")

    return area

@areas.post('/',name="Crear área", response_model=AreaRead, status_code=201)
async def create_chemical(
    area: AreaCreate = Body(..., title="Datos del árer", description="Datos del área a crear"),
    active_user = Depends(get_current_user)
    )->dict:
    """
    Crea una área. Retorna el área creada.
    """
    await validate_role(active_user)
    await db_validation(data_in= area, field_to_validate="area", collection=areas_collection)
    await multiple_db_validation(data_in= area, field_to_validate="chemicals", collection=chemicals_collection)
    area = set_status(area)
    area = set_update_info(area, active_user)
    area = await drop_inactive_nested_ids(area, "chemicals", chemicals_collection)
    new_area = await create_document(area, areas_collection)
    new_area = await populate(new_area, "chemicals", chemicals_collection, "chemical")
    new_area = await populate(new_area, "last_update_by", users_collection, "username")
    return new_area

@areas.put('/{id}',name="Actualizar área", response_model=AreaRead, status_code=202)
async def update_chemical(
    id: PyObjectId =  Path(..., title="ID del área", description="El MongoID del área a actualizar"),
    new_data: AreaUpdate = Body(..., title="Datos Nuevos", description="Nueva información a actualizar al área."),
    active_user = Depends(get_current_user)
    )->dict:
    """
    Actualiza los datos del área del ID ingresado. Retorna el área actualizada.
    """
    await validate_area_auth(active_user, id)
    await db_validation(collection=areas_collection, check_duplicate=False, search_id=True, query_value=id)
    await db_validation(data_in=new_data, field_to_validate= "area", collection= areas_collection)
    await multiple_db_validation(data_in=new_data, field_to_validate="chemicals", collection=chemicals_collection)
    new_data = set_update_info(new_data, active_user)
    new_data = await drop_inactive_nested_ids(new_data, "chemicals", chemicals_collection)
    updated_area = await update_document(id, areas_collection, new_data)    
    updated_area = await populate(updated_area, "chemicals", chemicals_collection, "chemical")
    updated_area = await populate(updated_area, "last_update_by", users_collection, "username")
    return updated_area

@areas.delete("({id}", name="Eliminar o restaurar área", response_model=AreaRead, status_code=200)
async def delete_restore_user(id: PyObjectId, active_user = Depends(get_current_user))->dict:
    """
    Cambia el área correspondiente al ID ingresado a inactivo (False) o activo (True).
    """
    await validate_role(active_user)
    await db_validation(collection=areas_collection, check_duplicate=False, search_id=True, query_value=id)
    deleted_area = await delete_restore_document(id, areas_collection, active_user, users_collection, "areas")
    deleted_area = await populate(deleted_area, "chemicals", chemicals_collection, "chemical")
    deleted_area = await populate(deleted_area, "last_update_by", users_collection, "username")
    return deleted_area