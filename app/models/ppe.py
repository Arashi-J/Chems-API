from pydantic import BaseModel, FileUrl

class Ppe(BaseModel):
    ppe: str
    img: FileUrl