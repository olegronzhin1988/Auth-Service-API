# database.py file, database settings

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings as stngs

# Database connection url for PostrgreSQL database
# with asyncpg driver
DATABASE_URL = f"postgresql+asyncpg://{stngs.POSTGRES_USER}:{stngs.POSTGRES_PASSWORD}@{stngs.POSTGRES_HOST}:{stngs.POSTGRES_PORT}/{stngs.POSTGRES_DB}"

# Async engine
engine = create_async_engine(DATABASE_URL)

# Session for the engine
# Expire_on_commit prevents auto expiration after commit
new_session = async_sessionmaker(engine, expire_on_commit = False)

# Parent class for project chart/sheet classes
class Model(DeclarativeBase):       # Model(MappedAsDataclass, DeclarativeBase):
    pass                            # if you want to turn a model into python dataclass. 
                                    # It`ll make all fields neccessary.
# Dependency function to get database session
async def get_db():
    async with new_session() as session:
        yield session

# Database session dependency. Provides session,
# closes it after
SessionDep = Annotated[AsyncSession, Depends(get_db)]