from enum import Enum

class QueryStatus(str, Enum):
    active = "activos"
    inactive = "inactivos"
    all = "todos"

class ApprovalType(str, Enum):
    ems = "ems"
    fsms = "fsms"
    ohsms = "ohsms"