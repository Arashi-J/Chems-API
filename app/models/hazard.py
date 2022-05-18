from pydantic import BaseModel, FileUrl

class Hazard(BaseModel):
    code: str
    hazard: str
    description: str
    precaution: str
    pictogram: FileUrl