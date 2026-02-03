from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.config.settings import get_settings
from src.infrastructure.database.session import get_db
from src.domains.auth.router import router as auth_router
from src.domains.users.router import router as users_router
from src.domains.recipients.router import router as recipients_router

settings = get_settings()

app = FastAPI(
    debug=settings.DEBUG,
    docs_url=settings.SWAGGER_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
    # swagger_ui_parameters={"persistAuthorization": True}
)

origins = [settings.FRONTEND_BASE_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(recipients_router)

@app.get("/")
async def root(db: Annotated[Session, Depends(get_db)]):
    return {
        "message": "Hello from FastAPI",
        "token": token
    }
