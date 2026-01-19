from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from src.config.settings import get_settings
from src.domains.auth.router import router as auth_router

settings = get_settings()

app = FastAPI(
    debug=settings.DEBUG,
    docs_url=settings.SWAGGER_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
)
app.include_router(auth_router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@app.get("/")
async def root(db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]):
    return {
        "message": "Hello from FastAPI",
        "token": token
    }
