from enum import Enum

class QueryStatus(str, Enum):
    active = "activos"
    inactive = "inactivos"
    all = "todos"