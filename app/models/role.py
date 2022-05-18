from pydantic import BaseModel

class Role(BaseModel):
    role: str
    role_name: str