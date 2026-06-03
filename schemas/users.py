# users.py schemas file, contain user schemas

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
from security import create_access_toker

# Base User schema
class SUserBase(BaseModel):
    username:str = Field(default=..., 
                         title="User name",
                         description="User name,  given at registration",
                         min_length=3,
                         max_length = 50)
    
    email:EmailStr = Field(default=...,
                           title="User email",
                           description="User email address, given at registration, used to log in")
    
# Pydantic Model setting, to work with ORM
    model_config = ConfigDict(from_arrtibutes=True)

# Register User schema
class SUserReg(SUserBase):
    password:str = Field(default=...,
                         title="User password",
                         description="User password, used to log in",
                         min_length=8)

# User Login schema 
class SUserLogin(BaseModel):
    email:EmailStr = Field(default=...,
                           title="User email",
                           description="User email address, given at registration, used to log in")

    password:str = Field(default=...,
                         title="User password",
                         description="User password, used to log in",
                         min_length=8)

# User Update schema
class SUserUpdate(BaseModel):
    username:str|None = Field(default=None, 
                              title="New user name",
                              description="New user name for update",
                              min_length=3,
                              max_length = 50)
    
    email:EmailStr|None = Field(default=None,
                           title="New user email",
                           description="New user email address, for update")

# User schema, used for response
class SUserResponse(SUserBase):
    id:int = Field(default=...,
                   title="User ID",
                   description="ID, given to user at creation",
                   ge=1)
    
    role:str = Field(default="user",
                     title="User role",
                     description="User role in the system, user or admin")

    is_active:bool = Field(default=True,
                           title="User status",
                           description="Current user status in the system, active or not")
    
    created_at:datetime= Field(default = datetime.now(),
                               title="User creation date & time",
                               description="Date and time when user was added to the system")
    
