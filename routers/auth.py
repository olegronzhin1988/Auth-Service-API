# auth.py router file. Contains router & endpoints for authentification

from fastapi import APIRouter, status, HTTPException
from database import SessionDep
from schemas.users import SUserBase, SUserLogin, SUserReg, SUserResponse, SUserUpdate
from schemas.tokens import SAccessToken, SRefreshTokenRequest, SToken
from models.users import UsersModel
from sqlalchemy import select, update
from datetime import datetime
from typing import Optional
from pydantic import EmailStr
import security as scrty
import redis.asyncio as redis
from config import Settings as stngs
import services.auth_service as au_srvc

# Authentification router
auth_router = APIRouter(prefix="/auth",
                        tags=["Authentification", "Users", "Tokens"])

# ENDPOINTS
# Register new department 
@auth_router.post("/register",
                  status_code=status.HTTP_201_CREATED,
                  description="Register new user")
async def user_register(session:SessionDep,
                       user_in: SUserReg) -> SToken:

# Calling service user register function     
    new_user = au_srvc.user_register(SessionDep, user_in)

# Calling service create tokens function
    access_token, refresh_token = au_srvc.create_tokens(new_user)
        
# Returning tokens
    return SToken(access_token = access_token, 
                  refresh_token = refresh_token)

# Email+password authentification
@auth_router.post("/login",
                  status_code=status.HTTP_200_OK,
                  description="Authentification via email and password")
async def user_login(session:SessionDep,
                     user_login = SUserLogin) -> SToken:    
# Creating dict for a login user
    user_dict = user_login.model_dump()

# Check there is no user with such name or email
    conditions =[]
    conditions.append(UsersModel.hashed_password == hash_password(user_dict["password"]))
    conditions.append(UsersModel.email == user_dict['email'])
    query = select(UsersModel).where(*conditions)
    result = await session.execute(query)
    user_found = result.scalar_one_or_none()
