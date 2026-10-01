import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.users.models import User

test_engine = create_async_engine(settings.test_database_url, echo=False, poolclass=NullPool,)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture(scope='function')
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope='function')
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
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

@pytest_asyncio.fixture
async def register_user(client: AsyncClient):
    counter = {'n': 0}

    async def _register(email: str | None = None, **overrides) -> dict:
        counter['n'] += 1
        credentials = {
            'email': email or f'user{counter['n']}@example.com',
            'password': 'somepassword123',
            'first_name': 'Test',
            'last_name': f'User{counter['n']}',
        }
        credentials.update(overrides)

        response = await client.post('/auth/register', json=credentials)
        assert response.status_code == 201, response.text
        credentials['id'] = response.json()['id']
        return credentials

    return _register


@pytest_asyncio.fixture
async def login_user(client: AsyncClient):
    async def _login(credentials: dict) -> dict:
        response = await client.post(
            '/auth/login',
            data={'username': credentials['email'], 'password': credentials['password']},
        )
        assert response.status_code == 200, response.text
        token = response.json()['access_token']
        return {'Authorization': f'Bearer {token}'}

    return _login


@pytest_asyncio.fixture
async def admin_user(register_user, db_session: AsyncSession) -> dict:
    credentials = await register_user(email='admin@example.com')

    user = await db_session.get(User, credentials['id'])
    user.is_admin = True
    await db_session.commit()

    return credentials


@pytest_asyncio.fixture
async def admin_headers(admin_user: dict, login_user) -> dict:
    return await login_user(admin_user)


@pytest_asyncio.fixture
async def create_team(client: AsyncClient, admin_headers: dict):
    counter = {'n': 0}

    async def _create(name: str | None = None) -> dict:
        counter['n'] += 1
        response = await client.post(
            '/teams',
            json={'name': name or f'Team {counter['n']}'},
            headers=admin_headers,
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _create