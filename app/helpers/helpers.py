from fastapi import HTTPException
from pydantic import BaseModel

from app.models.py_object_id import PyObjectId

async def populate(
    dict_to_populate: dict,
    field_with_nested_ids: str,
    collection,
    field_to_populate: str | None = None,
)->dict:
    """
    Remplaza los MongoID aninados en un lista por un diccionario de la forma {"id": id, "valor": valor} para un documento.
    """
    field: list | PyObjectId = dict_to_populate[field_with_nested_ids]
  
    if type(field) is list:
        populated_items = []
        for nested_id in field:
            item = await collection.find_one({"_id": nested_id})
            if not field_to_populate:
                populated_items.append(item)
            if field_to_populate:
                populated_items.append(
                    {"id": nested_id, field_to_populate: item[field_to_populate]}
                )
        
        dict_to_populate.update({field_with_nested_ids: populated_items})
    
    else:
        item = await collection.find_one({"_id": field})      
        if not field_to_populate:
            populated_item = item
        if field_to_populate:
            populated_item = {"id": field, field_to_populate: item[field_to_populate]}      
        
        dict_to_populate.update({field_with_nested_ids: populated_item})
        
    return dict_to_populate

async def multiple_populate(
    documents: list,
    field_with_nested_ids: str,
    collection,
    field_to_populate: str | None = None,
):
    """
    Remplaza los MongoID aninados en una lista por un diccionario de la forma {"id": id, "valor": valor} para varios documentos en una lista.
    """

    documents = [
        await populate(
            document, field_with_nested_ids, collection, field_to_populate
        )
        for document in documents
    ]
    return documents

async def db_validation(
    data_in: BaseModel,
    field_to_validate: str,
    collection,
    check_duplicate: bool = True,
    search_id: bool = False,
    query_value: str | None = None
    )->None:
    """
    Verifica que los campos con Mongo IDs no sean duplicados o tengan un valor válido, depediendo si el parámetro check_duplicate es True o False.
    """
    if not query_value:
        query_value = data_in.dict()[field_to_validate]

    query = {"_id": query_value} if search_id else {field_to_validate: query_value}
    
    result = await collection.find_one(query)

    if check_duplicate and result:
            raise HTTPException(status_code=400, detail=f"{query} ya se encuentra en la base de datos")

    if not check_duplicate and not result:
        raise HTTPException(status_code=400, detail=f"La información ingresada en el campo {field_to_validate} no es válida. {query} no se encuentra en la base de datos.")

async def multiple_db_validation(
    data_in: BaseModel,
    field_to_validate: str,
    collection,
    )->None:
    """
    Verifica en un iterable que los con Mongo IDs en el campo iterable tengan un valor válido.
    """
    for nested_id in data_in.dict()[field_to_validate]:
        await db_validation(data_in, field_to_validate, collection, False, True, nested_id)

#TODO: Quitar duplicados en área

def drop_duplicates(document: BaseModel, field_with_duplicates: str):
    
    document_dict = document.dict()

    document_dict[field_with_duplicates] = list(set(document_dict[field_with_duplicates]))
    
    document = document.parse_obj(document_dict)

    return document