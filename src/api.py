from fastapi import FastAPI
from src.domain.users.controller import router as users_router

def register_routes(app: FastAPI):
    app.include_router(users_router)