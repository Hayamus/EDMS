import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient, registered_user: dict):
    login_response = await client.post(
        '/auth/login',
        data={'username': registered_user['email'], 'password': registered_user['password']},
    )
    assert 'refresh_token' in login_response.cookies

    logout_response = await client.post('/auth/logout')

    assert logout_response.status_code == 204


@pytest.mark.asyncio
async def test_refresh_fails_after_logout(client: AsyncClient, registered_user: dict):
    await client.post(
        '/auth/login',
        data={'username': registered_user['email'], 'password': registered_user['password']},
    )
    await client.post('/auth/logout')

    response = await client.post('/auth/refresh')

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_without_cookie_is_idempotent(client: AsyncClient):
    response = await client.post('/auth/logout')

    assert response.status_code == 204