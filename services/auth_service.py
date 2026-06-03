# auth-service.py file, contains service functions for authentification

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
import redis.asyncio as redis

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
                            detail =f"User with username {user_dict["username"]} and/or email {user_dict['email']} already exists")

# Registrating user
    else:
        user_dict["hashed_password"] = hash_password(user_dict["password"])
        del user_dict["password"]
        user_dict["created_at"] = datetime.now()
        new_user = UsersModel(**user_dict)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

# Returning registrated user to router
        return new_user
    
async def create_tokens(user:UsersModel):
# Creating tokens
    access_token = scrty.create_access_token({"sub":str(user.id)})
    refresh_token = scrty.create_refresh_token({"sub":str(user.id)})

# Saving refresh token to Redis
    await redis.redis_client.setex(
        f"refresh{user.id}",
        stngs.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        refresh_token)

    return access_token, refresh_token