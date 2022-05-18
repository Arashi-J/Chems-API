from motor.motor_asyncio import AsyncIOMotorClient
import certifi

from core.config import get_settings

client = AsyncIOMotorClient(get_settings().CONNECTION_STRING, tlsCAFile=certifi.where())

db = client["ChemApp_DB"]



