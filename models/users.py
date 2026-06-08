# users.py model file, contains table model for users

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from typing import List, Optional
from database import Model
from datetime import datetime

class UsersModel(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user") # "user"| "admin"
    is_active: Mapped[bool] = mapped_column(default = True)
    created_at: Mapped[datetime] = mapped_column(default = datetime.now)