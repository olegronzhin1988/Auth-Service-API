# auth_service.py file, contains service functions for authentification
# and user_register

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from schemas.users import SUserBase, SUserLogin, SUserReg, SUserResponse, SUserUpdate
from models.users import UsersModel
from sqlalchemy import select, update
from datetime import datetime
from typing import Optional
from pydantic import EmailStr
from config import Settings as stngs
import security as scrty
from dependencies import redis_client

# User register service function
async def user_register(session:AsyncSession, user_in:SUserReg) -> UsersModel:
# Creating dict for a new user registration
    user_dict = user_in.model_dump()
    user_dict["username"] = user_dict["username"].strip()

# Check there is no user with such name or email
    conditions = []
    conditions.append(UsersModel.username == user_dict["username"])
    conditions.append(UsersModel.email == user_dict['email'])
    query = select(UsersModel).where(*conditions)
    result = await session.execute(query)
    user_found = result.scalar_one_or_none()

# Exception if there is any
    if user_found:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User with username {user_dict["username"]} and/or email {user_dict['email']} already exists")

# Registrating user
    else:
        user_dict["hashed_password"] = scrty.hash_password(user_dict["password"])
        del user_dict["password"]
        user_dict["created_at"] = datetime.now()
        new_user = UsersModel(**user_dict)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

# Returning registrated user to router
        return new_user

# Create access and refresh tokens function
async def tokens_create(user:UsersModel):
# Creating tokens
    access_token = scrty.create_access_token({"sub":str(user.id)})
    refresh_token = scrty.create_refresh_token({"sub":str(user.id)})

# Saving refresh token to Redis
    await redis_client.setex(
        f"refresh{user.id}",
        stngs.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        refresh_token)
# Returning created tokens
    return access_token, refresh_token

# Login via email and password function
async def user_login(session: AsyncSession, user_in:SUserLogin) -> None:

# Check there is no user with such name or email
    query = select(UsersModel).where(UsersModel.email == user_in.email)
    result = await session.execute(query)
    user_found = result.scalar_one_or_none()

    if not user_found or not scrty.verify_password(user_in.password, user_found.hashed_password):
        raise HTTPException(status=status.HTTP_401_UNAUTHORIZED,
                            detai="Incorrect email or password")
    else:
        if not user_found.is_active:
            raise HTTPException(status=status.HTTP_403_FORBIDDEN,
                                detail="Account deactivated")

# User Logout 
async def user_logout(access_token:str,
                      refresh_token:str,
                      user_in:UsersModel) -> None:
# Add access token to blacklist
    await redis.redis_client.setex(f"blacklist:{access_token}",
                                   stngs.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                                   "1")
    await redis.redis_client.delete(f"refresh:{user_in.id}")

# refresh user access token
async def refresh_access_token(refresh_token:str) -> str:
# Check refresh token
    try:
        payload = scrty.decode_token(refresh_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid refresh token")

# Check if it is refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token type")

# Check if there is such token in Redis
    user_id = payload.get("sub")
    stored_token = await redis_client.get(f"refresh:{user_id}")
    if not stored_token or stored_token != refresh_token:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="This refresh token is revoked")
    return scrty.create_refresh_token({"sub":user_id})