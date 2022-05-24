from fastapi import APIRouter

areas = APIRouter(prefix="/areas", tags=["Áreas"])

@areas.get('/', name="Obtener usuarios", response_model=list[UserRead], status_code=200)
async def get_users(
    skip: int = Query(0, title="Salto de página", description="Índica desde el cual número de documento inicia la consulta a la base de datos"),
    limit: int = Query(10, title="Límite", description="Índica la cantidad máxima que obtendrá la consulta a la Base de Datos"),
    status: QueryStatus = Query(QueryStatus.all, title="Estado", description="Determina si se requiere que la consulta obtenga los usuarios activos, inactivos o todos"),
    active_user: UserRead = Depends(get_current_user)
    )->list:
    """
    Obtiene todos los usuarios en la base de datos.
    """
    await validate_role(active_user)
    users = await get_documents(users_collection, skip, limit, status)
    users = await multiple_populate(users, "areas", areas_collection, "area")
    users = await multiple_populate(users, "role", roles_collection)
    return users

@areas.get('/{id}',name="Obtener usuario", response_model=UserRead, status_code=200)
async def get_user(
    id: PyObjectId = Path(..., title="ID del Usuario", description="El MongoID del usuario a buscar"),
    active_user: UserRead = Depends(get_current_user)
    )->dict:
    """
    Obtiene el usuario correspondiente al ID ingresado.
    """
    await validate_role(active_user)
    await db_validation(None, None, users_collection, False, True, id)
    user = await get_document_by_id(id, users_collection)
    user = await populate(user, "areas", areas_collection, "area")
    user = await populate(user, "role", roles_collection)
    return user

@areas.post('/',name="Crear usuario", response_model=UserRead, status_code=201)
async def create_user(
    user: UserCreate = Body(..., title="Datos del Usuario", description="Datos del usuario a crear"),
    active_user: UserRead = Depends(get_current_user)
    )->dict:
    """
    Crea un usuario. Retorna el usuario Creado.
    """
    await validate_role(active_user)
    await db_validation(user, "username", users_collection)
    await db_validation(user, "email", users_collection)
    await db_validation(user, "role", roles_collection, False, True)
    await multiple_db_validation(user, "areas", areas_collection)
    new_user = await create_documents(user, users_collection)
    new_user = await populate(new_user, "areas", areas_collection, "area")
    new_user = await populate(new_user, "role", roles_collection)
    return new_user

@areas.put('/{id}',name="Actualizar usuario", response_model=UserRead, status_code=202)
async def update_user(
    id: PyObjectId =  Path(..., title="ID del Usuario", description="El MongoID del usuario a actualizar"),
    new_data: UserUpdate = Body(..., title="Datos Nuevos", description="Nueva información a actualizar al usuario."),
    active_user: UserRead = Depends(get_current_user)
    )->dict:
    """
    Actualiza los datos del Usuario con el ID ingresado. Retorna el usuario actualizado.
    """
    await validate_role(active_user)
    await db_validation(None, None, users_collection, False, True, id)
    await db_validation(new_data, "username", users_collection)
    await db_validation(new_data, "email", users_collection)
    await db_validation(new_data, "role", roles_collection, False, True)
    await multiple_db_validation(new_data, "areas", areas_collection)
    updated_user = await update_document(id, users_collection, new_data)    
    updated_user = await populate(updated_user, "areas", areas_collection, "area")
    updated_user = await populate(updated_user, "role", roles_collection)
    return updated_user