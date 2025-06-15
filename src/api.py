from fastapi import FastAPI
from src.domain.users.controller import router as users_router
from src.domain.auth.controller import router as auth_router

def register_routes(app: FastAPI):
    app.include_router(users_router)
    app.include_router(auth_router)