import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditLog, AuditAction


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    payload = {
        'email': 'john@example.com',
        'password': 'strongpassword123',
        'first_name': 'John',
        'last_name': 'Smith',
    }

    response = await client.post('/auth/register', json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data['email'] == 'john@example.com'
    assert data['first_name'] == 'John'
    assert data['last_name'] == 'Smith'
    assert 'password' not in data
    assert 'password_hash' not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        'email': 'bob@example.com',
        'password': 'somepassword123',
        'first_name': 'Bob',
        'last_name': 'Jones',
    }

    first = await client.post('/auth/register', json=payload)
    assert first.status_code == 201

    second = await client.post('/auth/register', json=payload)
    assert second.status_code == 400
    assert 'already exists' in second.json()['detail'].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    payload = {
        'email': 'not-an-email',
        'password': 'somepassword123',
        'first_name': 'Bob',
        'last_name': 'Jones',
    }

    response = await client.post('/auth/register', json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_password_too_short(client: AsyncClient):
    payload = {
        'email': 'short@example.com',
        'password': '1234567',
        'first_name': 'Bob',
        'last_name': 'Jones',
    }

    response = await client.post('/auth/register', json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_creates_audit_entry(client: AsyncClient, db_session: AsyncSession):
    payload = {
        'email': 'lil@example.com',
        'password': 'strongpassword123',
        'first_name': 'Lil',
        'last_name': 'Peep',
    }

    response = await client.post('/auth/register', json=payload)
    user_id = response.json()['id']

    result = await db_session.execute(
        select(AuditLog).where(AuditLog.action == AuditAction.USER_REGISTERED)
    )
    entries = result.scalars().all()

    assert len(entries) == 1
    assert entries[0].user_id == user_id