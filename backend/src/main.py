from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine, text

from .settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code
    engine = create_engine(str(settings.database_url))
    with engine.connect() as conn:
        conn.execute(
            text("CREATE TABLE IF NOT EXISTS test (id SERIAL PRIMARY KEY, name TEXT)")
        )
        conn.commit()
    yield
    # shutdown code

app = FastAPI(debug=settings.debug, lifespan=lifespan)

@app.get("/")
async def root():
    engine = create_engine(str(settings.database_url))
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM test")).fetchall()
    return {
        "message": "Hello FastAPI with Settings",
        "data": [dict(row) for row in result],
    }
