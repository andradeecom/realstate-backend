from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.database.core import init_db
from .api import register_routes
from src.logging import configure_logging, LogLevels

# Configure logging
configure_logging(LogLevels.info)

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Real Estate API",
    description="Multitenant Real Estate Application API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routes(app)