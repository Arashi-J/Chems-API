from fastapi import APIRouter, Query, Depends, Body, Path

from app.core.auth import get_current_user, validate_role
from app.crud.crud import create_document, delete_restore_document, get_document_by_id, get_documents, update_document
from app.db.database import db
from app.helpers.helpers import approval_validator, db_validation, multiple_db_validation, multiple_populate, populate, get_approval_info, set_status, set_update_info
from app.models.area import AreaRead
from app.models.chemical import ChemicalCreate, ChemicalRead, ChemicalUpdate
from app.models.hazard import Hazard
from app.models.ppe import Ppe
from app.models.py_object_id import PyObjectId
from app.models.enums import ApprovalType, QueryStatus

chemicals = APIRouter(prefix="/chemicals", tags=["Sustancias Químicas"])

chemicals_collection = db.chemicals
hazards_collection = db.hazards
ppes_collection = db.ppes
users_collection = db.users
areas_collection = db.areas

@chemicals.get('/', name="Obtener sustancias químicas", response_model=list[ChemicalRead], status_code=200, dependencies=[Depends(get_current_user)])
async def get_chemicals(
    skip: int = Query(0, title="Salto de página", description="Índica desde el cual número de documento inicia la consulta a la base de datos"),
    limit: int | None = Query(None, title="Límite", description="Índica la cantidad máxima que obtendrá la consulta a la Base de Datos"),
    status: QueryStatus = Query(QueryStatus.all, title="Estado", description="Determina si se requiere que la consulta obtenga los químicos activos, inactivos o todos"),
    )->list:
    """
    Obtiene todas las sustancias químicas en la base de datos.
    """
    chemicals = await get_documents(chemicals_collection, skip, limit, status)
    chemicals = await multiple_populate(chemicals, "hazards", hazards_collection)
    chemicals = await multiple_populate(chemicals, "ppes", ppes_collection)
    chemicals = await multiple_populate(chemicals, "last_update_by", users_collection)
    return chemicals

@chemicals.get('/{id}',name="Obtener sustancia química", response_model=ChemicalRead, status_code=200, dependencies=[Depends(get_current_user)])
async def get_chemical(
    id: PyObjectId = Path(..., title="ID de la sustancia química", description="El MongoID de la sustancia química a buscar"),
    )->dict:
    """
    Obtiene la sustancia química correspondiente al ID ingresado.
    """
    await db_validation(collection= chemicals_collection, check_duplicate=False, search_id=True, query_value=id)
    chemical = await get_document_by_id(id, chemicals_collection)
    chemical = await populate(chemical, "hazards", hazards_collection)
    chemical = await populate(chemical, "ppes", ppes_collection)
    chemical = await populate(chemical, "last_update_by", users_collection)
    chemical['fsms'] = await populate( chemical['fsms'], 'approbed_by', users_collection)
    chemical['ems'] = await populate( chemical['ems'], 'approbed_by', users_collection)
    chemical['ohsms'] = await populate( chemical['ohsms'], 'approbed_by', users_collection)
    return chemical

@chemicals.post('/',name="Crear sustancia química", response_model=ChemicalRead, status_code=201)
async def create_chemical(
    chemical: ChemicalCreate = Body(..., title="Datos del la sustancia química", description="Datos de la sustancia química a crear"),
    active_user = Depends(get_current_user)
    )->dict:
    """
    Crea una sustancia química. Retorna la sustancia química creada.
    """
    await db_validation(data_in=chemical, field_to_validate="chemical", collection= chemicals_collection)
    await multiple_db_validation(data_in=chemical, field_to_validate="hazards", collection= hazards_collection)
    await multiple_db_validation(data_in=chemical, field_to_validate="ppes", collection= ppes_collection)
    chemical = set_status(chemical)
    chemical = set_update_info(chemical, active_user)
    chemical.update(await get_approval_info())
    new_chemical = await create_document(chemical, chemicals_collection)
    new_chemical = await populate(new_chemical, "hazards", hazards_collection)
    new_chemical = await populate(new_chemical, "ppes", ppes_collection)
    new_chemical = await populate(new_chemical, "last_update_by", users_collection)
    return new_chemical

@chemicals.put('/{id}',name="Actualizar sustancia química", response_model=ChemicalRead, status_code=202)
async def update_chemical(
    id: PyObjectId =  Path(..., title="ID de la sustancia química", description="El MongoID de la sustancia química a actualizar"),
    new_data: ChemicalUpdate = Body(..., title="Datos Nuevos", description="Nueva información a actualizar a la sustancia química."),
    active_user = Depends(get_current_user)
    )->dict:
    """
    Actualiza los datos de la sustancia química del ID ingresado. Retorna la sustancia química actualizada.
    """
    await db_validation(collection= chemicals_collection, check_duplicate=False, search_id=True, query_value=id)
    await db_validation(data_in=new_data, field_to_validate="chemical", collection=chemicals_collection)
    await multiple_db_validation(data_in=new_data, field_to_validate="hazards", collection=hazards_collection)
    await multiple_db_validation(data_in=new_data, field_to_validate="ppes", collection=ppes_collection)
    new_data = set_update_info(new_data, active_user)
    updated_chemical = await update_document(id, chemicals_collection, new_data)    
    updated_chemical = await populate(updated_chemical, "hazards", hazards_collection)
    updated_chemical = await populate(updated_chemical, "ppes", ppes_collection)
    updated_chemical = await populate(updated_chemical, "last_update_by", users_collection)
    return updated_chemical

@chemicals.delete("/{id}", name="Eliminar o restaurar sustancia química", response_model=ChemicalRead, status_code=200)
async def delete_restore_user(id: PyObjectId, active_user = Depends(get_current_user))->dict:
    """
    Cambia el estado de la sustancia química correspondiente al ID ingresado a inactivo (False) o activo (True).
    """
    await validate_role(active_user)
    await db_validation(collection= chemicals_collection, check_duplicate=False, search_id=True, query_value=id)
    deleted_chemical = await delete_restore_document(id, chemicals_collection, active_user,  areas_collection, "chemicals")
    deleted_chemical = await populate(deleted_chemical, "hazards", hazards_collection)
    deleted_chemical = await populate(deleted_chemical, "ppes", ppes_collection)
    deleted_chemical = await populate(deleted_chemical, "last_update_by", users_collection)
    return deleted_chemical

@chemicals.patch('/approval/{id}', name="Aprobar sustancia química", response_model=ChemicalRead, status_code=202)
async def chemical_approval(
    id: PyObjectId = Path(..., title="ID de la sustancia química", description="El MongoID de la sustancia química a aprobar"),
    approval_type: ApprovalType = Query(..., title="Tipo de Aprobación", description="Determina para qué sistema de gestión se reailizará la aprobación"),
    active_user = Depends(get_current_user)    
    )->dict:
    await validate_role(active_user, ["ems_approver", "fsms_approver", "ohsms_approver"])
    await db_validation(collection= chemicals_collection, check_duplicate=False, search_id=True, query_value=id)
    await approval_validator(id, approval_type)
    approved_chemical = await update_document(id, chemicals_collection, await get_approval_info(active_user, approval_type))    
    approved_chemical = await populate(approved_chemical, "hazards", hazards_collection)
    approved_chemical = await populate(approved_chemical, "ppes", ppes_collection)
    approved_chemical = await populate(approved_chemical, "last_update_by", users_collection)
    return approved_chemical

@chemicals.get('/hazards/', name="Obtener peligros", response_model=list[Hazard], status_code=200, dependencies=[Depends(get_current_user)])
async def get_chemicals(
    )->list:
    """
    Obtiene todos los peligros en la base de datos.
    """
    hazards = await get_documents(hazards_collection)
    return hazards

@chemicals.get('/hazards/{id}',name="Obtener peligro", response_model=Hazard, status_code=200, dependencies=[Depends(get_current_user)])
async def get_chemical(
    id: PyObjectId = Path(..., title="ID del peligro", description="El MongoID del peligro a buscar"),
    )->dict:
    """
    Obtiene el peligro correspondiente al ID ingresado.
    """
    await db_validation(collection=hazards_collection, check_duplicate=False, search_id=True, query_value=id)
    hazard = await get_document_by_id(id, hazards_collection)
    return hazard

@chemicals.get('/ppes/', name="Obtener EPPs", response_model=list[Ppe], status_code=200, dependencies=[Depends(get_current_user)])
async def get_chemicals(
    )->list:
    """
    Obtiene todos los EPP en la base de datos.
    """
    ppes = await get_documents(ppes_collection)
    return ppes

@chemicals.get('/ppes/{id}',name="Obtener EPP", response_model=Ppe, status_code=200, dependencies=[Depends(get_current_user)])
async def get_chemical(
    id: PyObjectId = Path(..., title="ID del EPP", description="El MongoID del EPP a buscar"),
    )->dict:
    """
    Obtiene el peligro correspondiente al ID ingresado.
    """
    await db_validation(collection=ppes_collection, check_duplicate=False, search_id=True, query_value=id)
    ppe = await get_document_by_id(id, ppes_collection)
    return ppe

@chemicals.get("/areas/{id}",name="Obtener áreas de la sustancia química", status_code=200, response_model=list[AreaRead], response_model_include={"id", "area"})
async def get_area_chemicals(id: PyObjectId, active_user = Depends(get_current_user))->list[dict]:
    """
    Obtiene todos los áreas en los que se encuentra la sustancia química del ID ingresado.
    """
    await validate_role(active_user)
    await db_validation(collection=chemicals_collection, check_duplicate=False, search_id=True, query_value=id)
    chemical_areas =  await areas_collection.find({"chemicals": id}).to_list(None)
    return chemical_areas