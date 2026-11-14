import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Request

from social_media.database import database, user_table
from social_media.models.user import UserIn
from social_media.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user,
    get_subject_for_token_type,
    create_confirmation_token
)

from social_media import tasks

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", status_code=201)
async def register(user: UserIn, background_task: BackgroundTasks, request: Request):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with email already exists"
        )
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)
    logger.debug(query)
    await database.execute(query)

    background_task.add_task(tasks.send_user_registration_email,
        user.email,
        confirmation_url=request.url_for("confirm_email", token=create_confirmation_token(user.email))
    )
    return {"detail": "User created. Please confirm your email."}


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirm/{token}")
async def confirm_email(token: str):
    email = get_subject_for_token_type(token, "confirmation")
    query = user_table.update().where(user_table.c.email == email).values(confirmed=True)

    logger.debug(query)
    await database.execute(query)
    return {"detail": "User confirmed"}