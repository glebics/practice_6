# tests/conftest.py

import pytest
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock
from app.main import app
from app.database import Base, get_db

DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"

# Создание тестового двигателя и сессии
engine = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def initialize_db() -> AsyncGenerator[None, None]:
    """
    Фикстура для инициализации базы данных перед тестами и её очистки после.

    Создаёт все таблицы перед тестами и удаляет их после завершения.
    """
    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Удаление таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(initialize_db) -> AsyncGenerator[AsyncSession, None]:
    """
    Фикстура для предоставления сессии базы данных для тестов.

    Возвращает объект AsyncSession, который используется в тестах.
    """
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def override_get_db(db_session: AsyncSession) -> Generator[None, None, None]:
    """
    Фикстура для переопределения зависимости `get_db` в приложении на тестовую сессию.

    Позволяет тестам использовать тестовую базу данных вместо реальной.
    """
    async def _get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def client(override_get_db: Generator[None, None, None]) -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура для предоставления тестового клиента HTTPX для взаимодействия с FastAPI приложением.

    Использует ASGITransport для асинхронного взаимодействия с приложением.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def crud_mock(mocker: Mock) -> Mock:
    """
    Фикстура для мокирования функции `get_dynamics` из модуля `app.crud`.

    Позволяет заменять реальную функцию на мок-объект в тестах.
    """
    return mocker.patch("app.crud.get_dynamics")
