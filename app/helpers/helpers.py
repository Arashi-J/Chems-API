from fastapi import HTTPException
from pydantic import BaseModel

async def populate(
    dict_to_populate: dict,
    field_with_nested_ids: str,
    collection,
    field_to_populate: str,
)->dict:
    """
    Remplaza los MongoID aninados en un lista por un diccionario de la forma {"id": id, "valor": valor} para un documento.
    """
    populated_items = []

    if type(dict_to_populate[field_with_nested_ids]) is not list:
        return dict_to_populate

    for nested_id in dict_to_populate[field_with_nested_ids]:
        item = await collection.find_one({"_id": nested_id})
        populated_items.append(
            {"id": nested_id, field_to_populate: item[field_to_populate]}
        )

    dict_to_populate.update({field_with_nested_ids: populated_items})

    return dict_to_populate

async def multiple_populate(
    documents: list,
    field_with_nested_ids: str,
    collection,
    field_to_populate: str,
):
    """
    Remplaza los MongoID aninados en una lista por un diccionario de la forma {"id": id, "valor": valor} para varios documentos en una lista.
    """
    if type(documents) is not list:
        return documents
    
    documents = [
        await populate(
            document, field_with_nested_ids, collection, field_to_populate
        )
        for document in documents
    ]
    return documents

async def db_validation(data_in: BaseModel, field_to_validate: str, collection)->None:
    """
    Valida si existen los valores indicados en la base de datos. Para verificar que los campos índice no sean duplicados.
    """
    query = {field_to_validate: data_in.dict()[field_to_validate]}
    result = await collection.find_one(query)
    if result:
        raise HTTPException(status_code=400, detail=f"{query} ya se encuentra en la base de datos")