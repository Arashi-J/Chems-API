from pydantic import BaseModel

class Phrase(BaseModel):
    code: str
    description: str