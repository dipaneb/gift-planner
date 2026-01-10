from fastapi import FastAPI
from sqlalchemy import create_engine, text
from .settings import settings

app = FastAPI()


@app.on_event("startup")
async def startup():
    engine = create_engine(str(settings.database_url))
    with engine.connect() as conn:
        conn.execute(
            text("CREATE TABLE IF NOT EXISTS test (id SERIAL PRIMARY KEY, name TEXT)")
        )
        conn.commit()


@app.get("/")
async def root():
    engine = create_engine(str(settings.database_url))
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM test")).fetchall()
    return {
        "message": "Hello FastAPI with Settings",
        "data": [dict(row) for row in result],
    }
