from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.teams.router import router as teams_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(teams_router)