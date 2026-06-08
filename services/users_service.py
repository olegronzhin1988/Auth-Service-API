# users_service.py file, contains user service functions
# exept user_register

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from schemas.users import SUserBase, SUserLogin, SUserReg, SUserResponse, SUserUpdate
from models.users import UsersModel
from sqlalchemy import select, update
from datetime import datetime
from typing import Optional
from pydantic import EmailStr
from config import settings as stngs
import security as scrty
import redis.asyncio as redis

# Service function to get list of all users, admin only
async def all_users_list(session: AsyncSession) -> list[SUserResponse]:
# Getting all users from database
    result = await session.execute(select(UsersModel))
    users_list = result.scalars().all()
    return users_list

# Service function to update user email or username
async def user_update(session: AsyncSession,
                      change_data:SUserUpdate,
                      current_user:UsersModel) -> SUserResponse:
# Check that email and/or username ar vacant:
    conditions = []
    if change_data.username:
        conditions.append(UsersModel.username == change_data.username)
    if change_data.email:
        conditions.append(UsersModel.email == change_data.email)
    query = select(UsersModel).where(*conditions)
    result = await session.execute(query)
    user_found = result.scalar_one_or_none()

# Exception if there is any
    if user_found and user_found.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User with username {change_data.username} and/or email {change_data.email} already exists")

# Update user
    else:
        values={}
        if change_data.username:
            values["username"] = change_data.username
        if change_data.email:
            values["email"] = change_data.email
        query = update(UsersModel).where(UsersModel.id == current_user.id).values(**values)
        await session.execute(query)
        await session.commit()
        await session.refresh(current_user)
        return current_user

# Service function to delete user
async def user_delete(session:AsyncSession,
                      user_id: int):
# Check that user with user_id exists in database
    user_found = await session.get(UsersModel, user_id)

# Exception: no user with such id
    if not user_found:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {user_id} doesn`t exist")

# User found, delete
    await session.delete(user_found)
    await session.commit()