from slowapi import Limiter
from slowapi.util import get_remote_address

# Key function: extracts the client IP (supports X-Forwarded-For behind a reverse proxy)
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
