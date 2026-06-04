# dependencies.py, used for redis tokens management

import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAutorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from config import settings as stngs
from database import SessionDep
from models.users import UsersModel
from security import decode_token

# redis client start
redis_client = redis.Redis(host=stngs.REDIS_HOST,
                           port=stngs.REDIS_PORT,
                           decode_responses=True)

bearer = HTTPBearer()

# Get current user service function
async def get_current_user(session: SessionDep,
                           credentials: HTTPAutorizationCredentials = Depends(bearer)) -> UsersModel:
    token = credentials.credentials

    if await redis_client.get(f"blacklist:{token}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has been revoked")
    
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail = "Invalid token")
    
    user = await session.get(UsersModel, int(user_id))

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not founf or inactive")

    return user

# Check current user role
def require_role(role:str):
    def checker(current_user: UsersModel = Depends(get_current_user)) -> UsersModel:
        if get_current_user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Insufficient permissions")
        return get_current_user
    return checker