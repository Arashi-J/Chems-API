from datetime import datetime

from pydantic import BaseModel

class Approval(BaseModel):
    approval: bool = False
    approver: str | None = None
    approval_date: datetime  | None = None