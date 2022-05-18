from pydantic import BaseModel, Field

class Role(BaseModel):
    role: str = Field(..., title='Rol', description="Valor único para identificar el rol")
    role_desc: str = Field(..., title='Nombre del Rol', description="Nombre completo del Rol")