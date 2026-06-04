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
from config import Settings as stngs
import security as scrty
import redis.asyncio as redis

# Service function to get list of all users, admin only
async def all_users_list(session: AsyncSession) -> list[SUserResponse]:
# Getting all users from database
    result = await session.execute(select(UsersModel))
    users_list = result.scalars().all()
    return users_list