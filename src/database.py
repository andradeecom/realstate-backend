import os
from databases import Database
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB=os.getenv("POSTGRES_DB")

if POSTGRES_PASSWORD is None:
    raise ValueError("POSTGRES_PASSWORD environment variable is not set")

DATABASE_URL=f'postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}'

database = Database(DATABASE_URL)