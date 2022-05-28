from datetime import datetime
from pydantic import BaseModel

from app.models.py_object_id import PyObjectId
from app.models.enums import QueryStatus, SearchKeys

async def get_documents(
    collection,
    skip: int = 0, 
    limit: int | None = None, 
    status: QueryStatus = QueryStatus.all,
    query_keys: SearchKeys | None = None, 
    query_value: str | None = None
    )->list:
    query = {"status": True} if status == QueryStatus.active else {"status": False} if status == QueryStatus.inactive else {}
    if query_keys and query_value:
        query_data = {"$or":[]}
        for seach_key in query_keys:
            query_data["$or"].append({seach_key: query_value})
        query.update(query_data)
    
    print(query)
    documents = await collection.find(query).skip(skip).to_list(limit)
    return documents
    
async def get_document_by_id(id: PyObjectId, collection)->dict:
    document = await collection.find_one({"_id": id})
    return dict(document)

async def get_document_by_query(query: dict, collection)->dict | None:
    document = await collection.find_one(query)
    try:
        return dict(document)
    except:
        return None

async def create_document(document: BaseModel, collection):  
    document = document.dict() if type(document) is not dict else document
    new_document = await collection.insert_one(document)
    created_document = await get_document_by_id(new_document.inserted_id, collection)
    return created_document

async def update_document(id: PyObjectId, collection, new_data: BaseModel | dict):
    if type(new_data) is not dict:
        new_data = new_data.dict(exclude_unset = True, exclude_none = True, exclude_defaults=True)
    else: 
        new_data = {k: v for k, v in new_data.items() if v}
    await collection.update_one({"_id": id}, {"$set": new_data})   
    updated_document = await get_document_by_id(id, collection)
    return updated_document


async def delete_restore_document(id: PyObjectId, collection, user: dict, collection_to_update = None, field_to_update: str | None = None,):
    
    deleted_document = await get_document_by_id(id, collection)
    current_status = deleted_document["status"]
    await collection.update_one({"_id": id}, {"$set": {
        "status": not current_status,
        "last_update_by": user["_id"],
        "last_update_date": datetime.utcnow()
        }})
    deleted_document = await get_document_by_id(id, collection)
    
    if field_to_update and current_status:
        documents_to_update = await collection_to_update.find({field_to_update: {"$all": [id]}}).to_list(None)
        for document in documents_to_update:
            updated_field = document[field_to_update]
            updated_field.remove(id)
            await collection_to_update.update_one({"_id": document["_id"]}, {"$set": {field_to_update: updated_field}})

    return deleted_document


#TODO: universal search
#TODO:  show areas where the chemical is used
