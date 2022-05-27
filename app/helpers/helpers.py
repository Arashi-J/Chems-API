from datetime import datetime
import re
import unicodedata
from fastapi import HTTPException
from pydantic import BaseModel
from app.crud.crud import get_document_by_id
from app.db.database import db
from app.models.approval import Approval
from app.models.enums import ApprovalType
from app.models.phrase import Phrase

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
    try:
        documents = [
            await populate(
                document, field_with_nested_ids, collection, field_to_populate
            )
            for document in documents
        ]
        return documents
    except:
        return documents

async def db_validation(*,
    data_in: BaseModel | None = None,
    field_to_validate: str | None = None,
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

    if query_value and not check_duplicate and not result:
        raise HTTPException(status_code=400, detail=f"La información ingresada en el campo {field_to_validate} no es válida. {query} no se encuentra en la base de datos.")

async def multiple_db_validation(
    data_in: BaseModel,
    field_to_validate: str,
    collection,
    )->None:
    """
    Verifica en un iterable que los con Mongo IDs en el campo iterable tengan un valor que exista en la base de datos.
    """
    list_to_populate = data_in.dict()[field_to_validate]

    if type(list_to_populate) is list and len(list_to_populate) > 0:
        try:
            for nested_id in list_to_populate:
                await db_validation(
                    data_in=data_in, field_to_validate=field_to_validate,
                    collection=collection, check_duplicate=False,
                    search_id=True, query_value=nested_id)
        except:
            raise HTTPException(status_code=400, detail=f"La información ingresada en el campo {field_to_validate} no es válida. {nested_id} no se encuentra en la base de datos.")

def text_normalizer_title(text:str)->str:

    text = text.title()
        
    nfkd_form = unicodedata.normalize('NFKD', text)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def text_normalizer_lower(text:str)->str:

    text = text.casefold()
        
    nfkd_form = unicodedata.normalize('NFKD', text)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def drop_duplicates(input: list)->list:
    """
    Elimina los elementos duplicados en los campos tipo lista o tupla.
    """
    try: 
        input = list(set(input))
    finally :
        return input

def p_phrase_code_normalizer(p_phrase: Phrase)->dict:
    
    p_phrase = p_phrase.dict()
    phrase_code = p_phrase["code"]
    phrase_code = "P" + re.sub("[^0-9]", "", phrase_code)
    p_phrase["code"] = phrase_code    

    return p_phrase

def h_phrase_code_normalizer(h_phrase: Phrase)->dict:
    
    h_phrase = h_phrase.dict()
    phrase_code = h_phrase["code"]
    phrase_code = "H" + re.sub("[^0-9]", "", phrase_code)
    h_phrase["code"] = phrase_code    

    return h_phrase

def set_update_info(item: dict | BaseModel, user: dict)->dict:
    item = item.dict() if type(item) is not dict else item
    item["last_update_date"] = datetime.utcnow()
    item["last_update_by"] = user["_id"]
    return item

def set_status(item: dict | BaseModel):
    item = item.dict() if type(item) is not dict else item
    item["status"] = True
    return item

async def get_approval_info(approver: dict | None = None, approval_type: ApprovalType | None = None)->dict:
    approval_info = {}
    
    if not approver:
        empty_approval = Approval().dict()
        approval_info[ApprovalType.ems] = empty_approval
        approval_info[ApprovalType.fsms] = empty_approval
        approval_info[ApprovalType.ohsms] = empty_approval

    if approver:
        approver_role = dict(await get_document_by_id(approver["role"], db.roles))["role"]
        approver_id = approver["_id"]

        if approval_type == ApprovalType.ems:
            if approver_role not in ["admin", "ems_approver"]:
                raise HTTPException(status_code=403, detail="El usuario no tiene el rol requerido para realizar esta acción")
            approval_info[ApprovalType.ems] = Approval(approval=True, approbed_by=approver_id, approval_date=datetime.utcnow()).dict()
        
        if approval_type == ApprovalType.fsms:
            if approver_role not in ["admin", "fsms_approver"]:
                raise HTTPException(status_code=403, detail="El usuario no tiene el rol requerido para realizar esta acción")
            approval_info[ApprovalType.fsms] = Approval(approval=True, approbed_by=approver_id, approval_date=datetime.utcnow()).dict()
        
        if approval_type == ApprovalType.ohsms:
            if approver_role not in ["admin", "ohsms_approver"]:
                raise HTTPException(status_code=403, detail="El usuario no tiene el rol requerido para realizar esta acción")
            approval_info[ApprovalType.ohsms] = Approval(approval=True, approbed_by=approver_id, approval_date=datetime.utcnow()).dict()
    
    return approval_info

async def approval_validator(id: PyObjectId, approval_type: ApprovalType)->None:
    approval = dict(await db.chemicals.find_one({"_id": id}))[approval_type]["approval"]
    if approval:
        raise HTTPException(status_code=400, detail="La sustancia ya tiene aprobación por parte de este sistema de gestión")
