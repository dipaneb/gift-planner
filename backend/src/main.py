from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from src.config.settings import settings


app = FastAPI(debug=settings.DEBUG)

@app.get("/")
async def root(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(text("SELECT * FROM test")).scalars().all()
    return {
        "result": result,
        "message": "Hello FastAPI with Settings",
        "data": [dict(row) for row in result],
    }
