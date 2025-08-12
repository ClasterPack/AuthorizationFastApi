from typing import Optional

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, HTTPException, status, Request

from src.app.dto.authorization import CreateUserDTO, TokenDTO, LoginUserDTO, UpdateTokenDTO, UpdatePasswordDTO, \
    UpdateUserDTO
from src.domain.entities.user import User
from src.infrastructure.postgres.uow import UnitOfWork
from src.services.jwt_utils import encode_jwt, decode_jwt, validate_pwd, hash_pwd

router = APIRouter()

async def get_user_by_login(uow, user_data):
    users = None
    if user_data.username is not None:
        users = await uow.user.filter(username=user_data.username)
    elif user_data.email is not None:
        users = await uow.user.filter(email=user_data.email)
    user = users[0] if users else None

    if not user or not validate_pwd(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )
    return user


@router.post("/registration", response_model=TokenDTO)
@inject
async def register_user(
    data: CreateUserDTO,
    uow: FromDishka[UnitOfWork],
):
    email = await uow.user.filter(email=data.email)
    username = await uow.user.filter(username=data.username)
    if email or username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already taken."
        )

    user = User.create(
        username=data.username,
        email=str(data.email),
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    created_user = await uow.user.create(user)
    await uow.commit()

    payload = {
        "sub": str(created_user.id),
        "username": created_user.username,
        "email": created_user.email,
        "token_version": created_user.token_version
    }
    access_token = encode_jwt(payload)

    return TokenDTO(
        token_type="Bearer",
        access_token=access_token,
        info="User registration was successful.",
    )

@router.post("/login", response_model=TokenDTO)
@inject
async def login_user(
    user_data: LoginUserDTO,
    uow: FromDishka[UnitOfWork],
):
    user = await get_user_by_login(uow, user_data)

    payload = {
        "sub": str(user.id), "email": user.email,
        "username": user.username , "token_version":user.token_version
    }
    access_token = encode_jwt(payload)

    return TokenDTO(
        token_type="Bearer",
        access_token=access_token,
        info="User logged in successfully.",
    )

@router.post("/refresh", response_model=TokenDTO)
@inject
async def refresh_token_endpoint(
    request: Request,
    uow: FromDishka[UnitOfWork],
    data: Optional[UpdateTokenDTO] = Body(default=None),
):
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    if not token and data:
        token = data.token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing."
        )

    try:
        payload = decode_jwt(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload.")

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token."
        )

    user = await uow.user.get(id=user_id)
    token_version = payload.get("token_version")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )
    if user.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token please update your access token."
        )

    new_refresh_token = encode_jwt(
        {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "token_version": user.token_version
        }
    )

    return TokenDTO(
        access_token=new_refresh_token,
        token_type="Bearer",
        info="Token refresh success.",
    )


@router.delete("/delete")
@inject
async def delete_user(
    uow: FromDishka[UnitOfWork],
    data: LoginUserDTO,
):
    user = await get_user_by_login(uow, data)


    await uow.user.drop(user.id)
    await uow.commit()
    return {"success": True, "message": f"User {user.username} has been deleted."}

@router.patch("/change_password")
@inject
async def change_password(
        uow: FromDishka[UnitOfWork],
        data: UpdatePasswordDTO,
):
    user = await get_user_by_login(uow, data)
    user.password = hash_pwd(data.new_password)
    user.token_version += 1
    await uow.user.update(user)
    await uow.commit()
    new_refresh_token = encode_jwt(
        {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "token_version": user.token_version
        }
    )

    return TokenDTO(
        access_token=new_refresh_token,
        token_type="Bearer",
        info="Password changed successfully."
    )

@router.patch("/update_user")
@inject
async def update_user(
        uow: FromDishka[UnitOfWork],
        data: UpdateUserDTO,
):
    user = await get_user_by_login(uow, data)
    updates = data.updates
    if updates.username is not None:
        user.username = updates.username
    if updates.email is not None:
        user.email = updates.email
    if updates.first_name is not None:
        user.first_name = updates.first_name
    if updates.last_name is not None:
        user.last_name = updates.last_name
    if updates.password is not None:
        user.password = hash_pwd(updates.password)
    user.token_version += 1
    await uow.user.update(user)
    await uow.commit()

    new_refresh_token = encode_jwt(
        {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "token_version": user.token_version
        }
    )
    return TokenDTO(
        access_token=new_refresh_token,
        token_type="Bearer",
        info="User was updated",
    )

