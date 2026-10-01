import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.teams.models.team_member import TeamMember

@pytest.fixture
def manager_in_team(create_team, register_user, login_user, client, db_session):
    async def _setup():
        team = await create_team()
        manager = await register_user()
        manager_headers = await login_user(manager)

        from app.teams.models.team_member import UserRole
        membership = TeamMember(user_id=manager['id'], team_id=team['id'], role=UserRole.MANAGER)
        db_session.add(membership)
        await db_session.commit()

        return team, manager, manager_headers

    return _setup

@pytest.mark.asyncio
async def test_add_member_success(
    client: AsyncClient, create_team, register_user, admin_headers: dict, db_session: AsyncSession
):
    team = await create_team()
    new_member = await register_user()

    response = await client.post(
        f'/teams/{team['id']}/members',
        json={'user_id': new_member['id']},
        headers=admin_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data['user_id'] == new_member['id']
    assert data['team_id'] == team['id']
    assert data['role'] == 'employee'

@pytest.mark.asyncio
async def test_add_member_wrong_team_forbidden(
    client: AsyncClient, create_team, register_user, login_user, db_session: AsyncSession
):
    from app.teams.models.team_member import TeamMember, UserRole

    team_a = await create_team(name='Team A')
    team_b = await create_team(name='Team B')

    manager_a = await register_user()
    manager_a_headers = await login_user(manager_a)

    db_session.add(TeamMember(user_id=manager_a['id'], team_id=team_a['id'], role=UserRole.MANAGER))
    await db_session.commit()

    victim = await register_user()

    response = await client.post(
        f'/teams/{team_b['id']}/members',
        json={'user_id': victim['id']},
        headers=manager_a_headers,
    )

    assert response.status_code == 403

    result = await db_session.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_b['id'],
            TeamMember.user_id == victim['id'],
        )
    )
    assert result.scalar_one_or_none() is None

@pytest.mark.asyncio
async def test_add_member_requires_sufficient_role(
    client: AsyncClient, create_team, register_user, login_user, db_session: AsyncSession
):
    from app.teams.models.team_member import TeamMember, UserRole

    team = await create_team()
    employee = await register_user()
    employee_headers = await login_user(employee)

    db_session.add(TeamMember(user_id=employee['id'], team_id=team['id'], role=UserRole.EMPLOYEE))
    await db_session.commit()

    victim = await register_user()

    response = await client.post(
        f'/teams/{team['id']}/members',
        json={'user_id': victim['id']},
        headers=employee_headers,
    )

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_add_member_duplicate(client: AsyncClient, create_team, register_user, admin_headers: dict):
    team = await create_team()
    member = await register_user()

    first = await client.post(
        f'/teams/{team['id']}/members', json={'user_id': member['id']}, headers=admin_headers
    )
    assert first.status_code == 200

    second = await client.post(
        f'/teams/{team['id']}/members', json={'user_id': member['id']}, headers=admin_headers
    )
    assert second.status_code == 400


@pytest.mark.asyncio
async def test_add_member_nonexistent_user(client: AsyncClient, create_team, admin_headers: dict):
    team = await create_team()

    response = await client.post(
        f'/teams/{team['id']}/members', json={'user_id': 999999}, headers=admin_headers
    )

    assert response.status_code == 404