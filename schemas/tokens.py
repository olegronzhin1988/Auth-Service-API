# tokens.py shemas file, contains token schemas

from pydantic import BaseModel

# login and registration token schema, passed out
class SToken(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str="bearer"

# Refresh token schema, passed out
class SAccessToken(BaseModel):
    access_token:str
    token_type:str="bearer"

# Refresh token shema, taken in
class SRefreshTokenRequest(BaseModel):
    refresh_token:str