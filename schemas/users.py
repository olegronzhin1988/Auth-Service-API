# users.py schemas file, contain user schemas

from pydantic import BaseModel, Field, ConfigDict, EmailStr, model_validator
from datetime import datetime

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
    model_config = ConfigDict(from_attributes=True)

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

# Validator to check that class object is not empty
    @model_validator(mode="after")
    def at_least_one_field(self) -> "SUserUpdate":
        if not self.username and not self.email:
            raise ValueError("No changes were given, provide at least one")
        return self

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
    
    created_at:datetime= Field(default_factory=datetime.now,
                               title="User creation date & time",
                               description="Date and time when user was added to the system")
    
