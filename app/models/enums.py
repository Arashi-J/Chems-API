from enum import Enum

class QueryStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    all = "all"

class ApprovalType(str, Enum):
    ems = "ems"
    fsms = "fsms"
    ohsms = "ohsms"

class SearchKeys(list, Enum):
    areas = ["area"]
    chemicals = ["chemical"]
    hazards = ["hazard", "code"]
    ppes = ["ppe"]
    roles = ["role", "role_name"]
    users = ["firstname", "lastname", "username"]

class Collections(str, Enum):
    areas = "areas"
    chemicals = "chemicals"
    hazards = "hazards"
    ppes = "ppes"
    roles = "roles"
    users = "users"