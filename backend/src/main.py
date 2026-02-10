from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.config.settings import get_settings
from src.config.logging import setup_logging
from src.core.rate_limit import limiter
from src.core.middlewares.request_logging import RequestLoggingMiddleware
from src.domains.auth.router import router as auth_router
from src.domains.users.router import router as users_router
from src.domains.recipients.router import router as recipients_router
from src.domains.gifts.router import router as gifts_router

settings = get_settings()

# ── Logging ──────────────────────────────────────────────
setup_logging(log_level=settings.LOG_LEVEL, env=settings.ENV)

# ── App ──────────────────────────────────────────────────
app = FastAPI(
    debug=settings.DEBUG,
    docs_url=settings.SWAGGER_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
    # swagger_ui_parameters={"persistAuthorization": True}
)

# ── Rate Limiting ────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Middleware (order matters: last added = first executed) ──
# 1. CORS — must be outermost to handle preflight OPTIONS requests
origins = [settings.FRONTEND_BASE_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 2. Trusted Host — reject requests with unexpected Host headers
allowed_hosts = [h.strip() for h in settings.ALLOWED_HOSTS.split(",") if h.strip()]
if allowed_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# 4. Request logging + request ID generation
app.add_middleware(RequestLoggingMiddleware)

# ── Routers ──────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(recipients_router)
app.include_router(gifts_router)
