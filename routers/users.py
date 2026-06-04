# users.py router file. Contains router & endpoints for users

from fastapi import APIRouter, status, Depends
from database import SessionDep
from schemas.users import SUserBase, SUserLogin, SUserReg, SUserResponse, SUserUpdate
from models.users import UsersModel
from sqlalchemy import select, update
from datetime import datetime
from typing import Optional
from pydantic import EmailStr
import security as scrty
import redis.asyncio as redis
from config import Settings as stngs
import services.users_service as usr_srvc
from dependencies import get_current_user, require_role

# Users router
users_router = APIRouter(prefix="/users",
                         tags=["Users"])

# ENDPOINTS
# Get current authorized user profile
@users_router.get("/me",
                   status_code=status.HTTP_200_OK,
                   description="Returns current authorized user profile")
async def user_me(current_user:UsersModel = Depends(get_current_user)) ->SUserResponse:
    return current_user

# Get list of all users, admin only
@users_router.get("/",
                  status_code=status.HTTP_200_OK,
                  description="Provides list of all users, admin only")
async def user_list(session: SessionDep, 
                    current_user:UsersModel = Depends(require_role("admin"))) -> list[SUserResponse]:
# Calling service user list function
    return await usr_srvc.all_users_list(session)

# Change curent user`s username or email
@users_router.patch("/me",
                    status_code=status.HTTP_200_OK,
                    description="Change curent user`s username or email")
async def user_change(session:SessionDep,
                      change_data:SUserUpdate,
                      current_user: UsersModel = Depends(get_current_user)) -> SUserResponse:
    