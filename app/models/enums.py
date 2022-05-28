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
    hazards = ["hazard"]
    ppes = ["ppe"]
    roles = ["role"]
    users = ["firstname", "lastname", "username"]

class Collections(str, Enum):
    areas = "areas"
    chemicals = "chemicals"
    hazards = "hazards"
    ppes = "ppes"
    roles = "roles"
    users = "users"