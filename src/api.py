from fastapi import FastAPI
from src.users.controller import router as users_router
from src.properties.controller import router as properties_router

def register_routes(app: FastAPI):
    app.include_router(users_router)
    app.include_router(properties_router)

