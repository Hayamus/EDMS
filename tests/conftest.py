import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db

test_engine = create_async_engine(settings.test_database_url, echo=False, poolclass=NullPool,)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
def user_credentials() -> dict:
    return {
        'email': 'chel@example.com',
        'password': 'chelsspassword1',
        'first_name': 'Chel',
        'last_name': 'White',
    }


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient, user_credentials: dict) -> dict:
    response = await client.post('/auth/register', json=user_credentials)
    assert response.status_code == 201
    return user_credentials