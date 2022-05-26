from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.routers.users import users
from app.routers.chemicals import chemicals
from app.routers.areas import areas
from app.core.config import get_settings

description = """
    Administre las sustancias químicas que se utilizan en su empresa
    """

tags_metadata = [
    {
    "name": "Usuarios",
    "description": """
        Administra las operaciones con los usuarios, incluyendo la autenticación y los roles.
    """
    },
        {
    "name": "Áreas",
    "description": """
        Administra las operaciones con las áreas.
    """
    },
    {
    "name": "Sustancias Químicas",
    "description": """
        Administra las operaciones con las sustancias químicas, incluyendo los peligros y los EPP.
    """
    }
]

app = FastAPI(
    title="Chem Manager",
    description=description,
    version="0.0.1",
    contact={
        "name": "Juan Perez",
        "url": "https://github.com/Arashi-J",
        "email": "juan.perez@mail.com"
        },
    license_info= 
    {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata
)

app.include_router(users)
app.include_router(chemicals)
app.include_router(areas)

#For serving static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# For serving Jinja Templates
templates = Jinja2Templates(directory="app/templates")


#CORS Configuration
origins = ["*"]

#Iniciate Enviroment Settings
get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Jinja template serve path operation
@app.get("/", status_code=200, include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})