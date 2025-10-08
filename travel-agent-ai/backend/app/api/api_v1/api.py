from fastapi import APIRouter
from .endpoints import auth, users, travel, agents

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(travel.router, prefix="/travel", tags=["Travel"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])