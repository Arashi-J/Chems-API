from pydantic import BaseModel
from fastapi import HTTPException

from models.py_object_id import PyObjectId
from models.query_status import QueryStatus

async def get_documents(collection, skip: int, limit: int, status:QueryStatus)->list:   
    query = {"status": True} if status == QueryStatus.active else {"status": False} if status == QueryStatus.inactive else {}
    documents = await collection.find(query).skip(skip).to_list(limit)
    return documents
    
async def get_document_by_id(id: PyObjectId, collection)->dict:
    document = await collection.find_one({"_id": id})
    if not document:
        raise HTTPException(status_code=404, detail=f"El documento con id {id} no fue encontrado en la base de datos")
    return dict(document)

async def create_documents(document: BaseModel, collection)->dict:
    document = document.dict()
    new_document = await collection.insert_one(document)
    created_document = await get_document_by_id(new_document.inserted_id, collection)
    return created_document

async def update_document(id: PyObjectId, collection, new_data: BaseModel)->dict:
    await get_document_by_id(id, collection)
    new_data = new_data.dict(exclude_unset = True, exclude_none = True)
    await collection.update_one({"_id": id}, {"$set": new_data})   
    updated_document = await get_document_by_id(id, collection)
    return updated_document