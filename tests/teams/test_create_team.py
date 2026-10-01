import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditLog, AuditAction
from app.teams.models.team_member import TeamMember


@pytest.mark.asyncio
async def test_create_team_success(client: AsyncClient, admin_headers: dict, db_session: AsyncSession):
    response = await client.post('/teams', json={'name': 'HR Department'}, headers=admin_headers)

    assert response.status_code == 201
    data = response.json()
    assert data['name'] == 'HR Department'

    result = await db_session.execute(
        select(TeamMember).where(TeamMember.team_id == data['id'])
    )
    members = result.scalars().all()
    assert len(members) == 1


@pytest.mark.asyncio
async def test_create_team_duplicate_name(client: AsyncClient, admin_headers: dict):
    await client.post('/teams', json={'name': 'Finance'}, headers=admin_headers)
    response = await client.post('/teams', json={'name': 'Finance'}, headers=admin_headers)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_team_requires_admin(client: AsyncClient, register_user, login_user):
    regular_user = await register_user()
    headers = await login_user(regular_user)

    response = await client.post('/teams', json={'name': 'Shadow IT'}, headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_team_requires_authentication(client: AsyncClient):
    response = await client.post('/teams', json={'name': 'No Auth'})

    assert response.status_code == 401