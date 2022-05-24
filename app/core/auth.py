from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

from app.core.config import get_settings
from app.core.security import verify_password
from app.db.database import db
from app.crud.crud import get_document_by_query
from app.models.token import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')

users_collection = db.users

async def authenticate_user(collection, username: str, password: str):
    user = await get_document_by_query({"username": username}, collection)
    if not user or not user["status"]:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().SECRET_KEY, algorithm=get_settings().ALGORITHM)
    return encoded_jwt


async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(users_collection, form_data.username, form_data.password)
    if not user:
         raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña no válidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data = {"sub": user["username"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    print (token_data.dict())
    user = await get_document_by_query(token_data.dict(), users_collection)
    if user is None:
        raise credentials_exception
    if not user["status"]:
        raise HTTPException(status_code=400, detail="Usuario Deshabilitado")
    return user

