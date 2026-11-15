from slowapi import Limiter
from slowapi.util import get_remote_address

# Key function: the client IP, read from request.client.host.
# Behind a reverse proxy (Traefik on Dokploy), request.client.host is the real visitor IP
# only if uvicorn trusts the proxy's X-Forwarded-For header: see FORWARDED_ALLOW_IPS in
# docker/Dockerfile.prod. Otherwise every visitor shares the proxy's IP, and so its limits.
limiter = Limiter(key_func=get_remote_address)
