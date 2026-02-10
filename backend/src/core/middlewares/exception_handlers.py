import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("api.error")


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unhandled exceptions.
    Logs the full traceback server-side but returns only a generic message to the client,
    preventing stack trace leakage in production.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
        extra={
            "request_id": request_id,
            "extra_data": {
                "method": request.method,
                "path": request.url.path,
            },
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
