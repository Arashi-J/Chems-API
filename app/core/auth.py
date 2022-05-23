from fastapi.security import OAuth2PasswordBearer

from app.core.security import verify_password
from app.db.database import db


oauth2 = OAuth2PasswordBearer(tokenUrl='login')


def authenticate_user(collection, username: str, password: str):
    user = collection.find_one({"username": username})
    if not user:
        return False
    user = dict(user)
    if not verify_password(password, user["password"]):
        return False
    return user
    
