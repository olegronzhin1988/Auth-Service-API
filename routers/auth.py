# auth.py router file. Contains router & endpoints for authentification

from fastapi import APIRouter, status, Depends
from database import SessionDep
from schemas.users import SUserBase, SUserLogin, SUserReg, SUserResponse, SUserUpdate
from schemas.tokens import SAccessToken, SRefreshTokenRequest, SToken
from models.users import UsersModel
import services.auth_service as au_srvc
from dependencies import get_current_user, bearer
from fastapi.security import HTTPAuthorizationCredentials
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
    new_user = await au_srvc.user_register(session, user_in)

# Calling service create tokens function
    access_token, refresh_token = await au_srvc.tokens_create(new_user)
        
# Returning tokens
    return SToken(access_token = access_token, 
                  refresh_token = refresh_token)

# Email+password login/authentification
@auth_router.post("/login",
                  status_code=status.HTTP_200_OK,
                  description="Login/authentification via email and password")
async def user_login(session:SessionDep,
                     user_login: SUserLogin) -> SToken:    
# Calling serivice user login function
    user = await au_srvc.user_login(session, user_login)

# Calling service create tokens function
    access_token, refresh_token = await au_srvc.tokens_create(user)
        
# Returning tokens
    return SToken(access_token = access_token, 
                  refresh_token = refresh_token)

# User logout, invalidates user tokens, requires authorization
@auth_router.post("/logout",
                  status_code=status.HTTP_200_OK,
                  description="User logout with tokens invalidation, authorization needed")
async def user_logout(token_data: SRefreshTokenRequest,
                      current_user:UsersModel = Depends(get_current_user),
                      credentials: HTTPAuthorizationCredentials = Depends(bearer)):
# Creating access token
    access_token = credentials.credentials

# Calling logout service function
    await au_srvc.user_logout(access_token,
                              token_data.refresh_token, 
                              current_user)
    
    return {"message" :"Logged out successfully"}

# Refresh access token via refresh token
@auth_router.post("/refresh",
                  status_code=status.HTTP_200_OK,
                  description=" Refresh access token via refresh token")
async def token_refresh(token_data:SRefreshTokenRequest) ->SAccessToken:
# Calling service refresh function
    access_token = await au_srvc.refresh_access_token(token_data.refresh_token)
    return SAccessToken(access_token=access_token)

