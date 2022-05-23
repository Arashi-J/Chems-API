from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from app.core.config import get_settings

from app.core.security import verify_password


oauth2 = OAuth2PasswordBearer(tokenUrl='login')


def authenticate_user(collection, username: str, password: str):
    user = collection.find_one({"username": username})
    if not user:
        return False
    user = dict(user)
    if not verify_password(password, user["password"]):
        return False
    return user
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow + expires_delta
    else:
        expire = datetime.utcnow + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().JWT_SK, algorithm=get_settings().ALGORITHM)
    return encoded_jwt