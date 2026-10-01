import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.teams.models.team_member import TeamMember, UserRole


@pytest.mark.asyncio
async def test_change_role_success(
    client: AsyncClient, create_team, register_user, admin_headers: dict, db_session: AsyncSession
):
    team = await create_team()
    member = await register_user()

    await client.post(f'/teams/{team['id']}/members', json={'user_id': member['id']}, headers=admin_headers)

    response = await client.patch(
        f'/teams/{team['id']}/members/{member['id']}',
        json={'role': 'approver'},
        headers=admin_headers,
    )

    assert response.status_code == 200, response.json()
    assert response.json()['role'] == 'approver'


@pytest.mark.asyncio
async def test_change_role_same_role_fails(
    client: AsyncClient, create_team, register_user, admin_headers: dict
):
    team = await create_team()
    member = await register_user()

    await client.post(f'/teams/{team['id']}/members', json={'user_id': member['id']}, headers=admin_headers)

    response = await client.patch(
        f'/teams/{team['id']}/members/{member['id']}',
        json={'role': 'employee'},
        headers=admin_headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_change_role_not_a_member(
    client: AsyncClient, create_team, register_user, admin_headers: dict
):
    team = await create_team()
    not_a_member = await register_user()

    response = await client.patch(
        f'/teams/{team['id']}/members/{not_a_member['id']}',
        json={'role': 'manager'},
        headers=admin_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_change_role_requires_sufficient_permissions(
    client: AsyncClient, create_team, register_user, login_user, db_session: AsyncSession, admin_headers: dict
):
    team = await create_team()
    employee = await register_user()
    employee_headers = await login_user(employee)

    db_session.add(TeamMember(user_id=employee['id'], team_id=team['id'], role=UserRole.EMPLOYEE))
    await db_session.commit()

    victim = await register_user()
    await client.post(f'/teams/{team['id']}/members', json={'user_id': victim['id']}, headers=admin_headers)

    response = await client.patch(
        f'/teams/{team['id']}/members/{victim['id']}',
        json={'role': 'manager'},
        headers=employee_headers,
    )

    assert response.status_code == 403