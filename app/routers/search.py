from fastapi import APIRouter, Query, Depends
from app.core.auth import get_current_user
from app.crud.crud import get_documents

from app.db.database import db
from app.helpers.helpers import multiple_populate
from app.models.enums import Collections, QueryStatus, SearchKeys
from app.models.area import AreaRead
from app.models.chemical import ChemicalRead
from app.models.hazard import Hazard
from app.models.ppe import Ppe
from app.models.role import Role
from app.models.user import UserRead

search = APIRouter(prefix="/search", tags=["Busqueda"])

areas_collection = db.areas
chemicals_collection = db.chemicals
users_collection = db.users
hazards_collection = db.hazards
ppes_collection = db.ppes
roles_collection = db.roles

@search.get(
    "/", name="Buscar", status_code=200, 
    response_model=list[UserRead] | list[AreaRead] | list[ChemicalRead] | list[Hazard] | list[Ppe] | list[Role], 
    dependencies=[Depends(get_current_user)])
async def search_item(
    collection_name: Collections,
    search_query: str,
    skip: int = Query(0, title="Salto de página", description="Índica desde el cual número de documento inicia la consulta a la base de datos"),
    limit: int | None = Query(None, title="Límite", description="Índica la cantidad máxima que obtendrá la consulta a la Base de Datos"),
    status: QueryStatus = Query(QueryStatus.all, title="Estado", description="Determina si se requiere que la consulta obtenga ítems activos, inactivos o todos. No funciona con Peligros (Hazards), Roles (Roles), EPPs (PPEs)"),
)->list:
    """
    Busca ítems de acuerdo a los parámetros suministrados
    """
    collection = None
    search_keys = None

    if collection_name == Collections.areas:
        collection = areas_collection
        search_keys = SearchKeys.areas
    if collection_name == Collections.chemicals:
        collection = chemicals_collection
        search_keys = SearchKeys.chemicals
    if collection_name == Collections.hazards:
        collection = hazards_collection
        search_keys = SearchKeys.hazards
        status = QueryStatus.all
    if collection_name == Collections.ppes:
        collection = ppes_collection
        search_keys = SearchKeys.ppes
        status = QueryStatus.all
    if collection_name == Collections.roles:
        collection = roles_collection
        search_keys = SearchKeys.roles
        status = QueryStatus.all
    if collection_name == Collections.users:
        collection = users_collection
        search_keys = SearchKeys.users


    results = await get_documents(
        collection=collection,
        skip=skip, 
        limit=limit,
        status=status,
        query_keys=search_keys,
        query_value=search_query)

    if collection_name == Collections.users:
        results = await multiple_populate(results, "areas", areas_collection, "area")
        results = await multiple_populate(results, "role", roles_collection)
        results = await multiple_populate(results, "last_update_by", users_collection, "username")

    if collection_name == Collections.areas:
        results = await multiple_populate(results, "chemicals", chemicals_collection, "chemical")
        results = await multiple_populate(results, "last_update_by", users_collection, "username")

    if collection_name == Collections.chemicals:
        results = await multiple_populate(results, "hazards", hazards_collection)
        results = await multiple_populate(results, "ppes", ppes_collection)
        results = await multiple_populate(results, "last_update_by", users_collection, "username")

    return results


