from enum import Enum

class QueryStatus(str, Enum):
    active = "activos"
    inactive = "inactivos"
    all = "todos"

class ApprovalType(str, Enum):
    fsms = "fsms"
    ems = "ems"
    ohsms = "ohsms"