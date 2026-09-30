import pytest
from httpx import AsyncClient
import jwt
from app.core.config import settings


@pytest.mark.asyncio
async def test_refresh_returns_new_access_token(client: AsyncClient, registered_user: dict):
    login_response = await client.post(
        '/auth/login',
        data={'username': registered_user['email'], 'password': registered_user['password']},
    )
    old_access_token = login_response.json()['access_token']

    refresh_response = await client.post('/auth/refresh')

    assert refresh_response.status_code == 200
    new_access_token = refresh_response.json()['access_token']
    new_payload = jwt.decode(new_access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    old_payload = jwt.decode(old_access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    assert new_payload["sub"] == old_payload["sub"]
    assert new_payload["type"] == "access"


@pytest.mark.asyncio
async def test_refresh_without_cookie_fails(client: AsyncClient):
    response = await client.post('/auth/refresh')

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotates_cookie(client: AsyncClient, registered_user: dict):
    login_response = await client.post(
        '/auth/login',
        data={'username': registered_user['email'], 'password': registered_user['password']},
    )
    old_refresh_cookie = login_response.cookies['refresh_token']

    await client.post('/auth/refresh')

    new_refresh_cookie = client.cookies.get('refresh_token')
    assert new_refresh_cookie != old_refresh_cookie


@pytest.mark.asyncio
async def test_old_refresh_token_rejected_after_rotation(client: AsyncClient, registered_user: dict):
    login_response = await client.post(
        '/auth/login',
        data={'username': registered_user['email'], 'password': registered_user['password']},
    )
    old_refresh_cookie = login_response.cookies['refresh_token']

    first_refresh = await client.post('/auth/refresh')
    assert first_refresh.status_code == 200

    response = await client.post(
        '/auth/refresh',
        cookies={'refresh_token': old_refresh_cookie},
    )
    assert response.status_code == 401