from sqlalchemy.orm import DeclarativeBase, sessionmaker
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config.config import config


DATABASE_URL = (
    f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}"
    f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
)

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    DATABASE_URL,
    echo= True if config.IS_PRODUCT == "False" else False
)

async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session()-> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker() as session:
        yield session
