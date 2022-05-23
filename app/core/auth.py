from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.config import get_settings
from app.core.security import verify_password
from app.db.database import db
from app.crud.crud import get_document_by_query
from app.models.token import TokenData

oauth2 = OAuth2PasswordBearer(tokenUrl='login')

users_collection = db.users

async def authenticate_user(collection, username: str, password: str):
    user = await get_document_by_query({"username": username}, collection)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user
    
async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow + expires_delta
    else:
        expire = datetime.utcnow + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().JWT_SK, algorithm=get_settings().ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudo validar las credenciales del usuario",
        headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        payload = jwt.decode(token, get_settings().SECRET_KEY, algorithms=get_settings().ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await get_document_by_query(token_data.dict(), users_collection)
    if user is None:
        raise credentials_exception
    return user