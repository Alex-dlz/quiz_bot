from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = f"sqlite+aiosqlite:///{os.getenv('DB_PATH')}"

engine = create_async_engine(
    url=DB_URL, 
    echo=True,  
    future=True
)


async_session = async_sessionmaker(
    engine, 
    expire_on_commit=False,  
    class_=AsyncSession
)


class Base(DeclarativeBase, AsyncAttrs):
    pass

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)