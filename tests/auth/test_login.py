import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditLog, AuditAction

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, registered_user: dict):
    response = await client.post(
        '/auth/login',
        data={'username': registered_user['email'], 'password': registered_user['password']},
    )

    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'
    assert 'refresh_token' in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, registered_user: dict):
    response = await client.post(
        '/auth/login',
        data={'username': registered_user['email'], 'password': 'totallywrongpassword'},
    )

    assert response.status_code == 401
    assert 'refresh_token' not in response.cookies


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        '/auth/login',
        data={'username': 'ghost@example.com', 'password': 'whatever123'},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_failure_creates_audit_entry(client: AsyncClient, db_session: AsyncSession):
    await client.post(
        '/auth/login',
        data={'username': 'nobody@example.com', 'password': 'whatever'},
    )

    result = await db_session.execute(
        select(AuditLog).where(AuditLog.action == AuditAction.USER_LOGIN_FAILED)
    )
    entries = result.scalars().all()

    assert len(entries) == 1
    assert entries[0].details['email'] == 'nobody@example.com'
    assert entries[0].user_id is None 


@pytest.mark.asyncio
async def test_login_success_creates_audit_entry(client: AsyncClient, db_session: AsyncSession, registered_user: dict):
    await client.post(
        '/auth/login',
        data={'username': registered_user['email'], 'password': registered_user['password']},
    )

    result = await db_session.execute(
        select(AuditLog).where(AuditLog.action == AuditAction.USER_LOGGED_IN)
    )
    entries = result.scalars().all()

    assert len(entries) == 1