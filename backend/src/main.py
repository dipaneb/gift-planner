from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from src.config.settings import settings
from src.domains.auth.router import router as auth_router


app = FastAPI(
    debug=settings.DEBUG,
    docs_url=settings.SWAGGER_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
)
app.include_router(auth_router)


@app.get("/")
async def root(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(text("SELECT * FROM test")).scalars().all()
    return {
        "result": result,
        "message": "Hello FastAPI with Settings",
        "data": [dict(row) for row in result],
    }
