import logging
import json
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for production environments."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add request_id if present (injected by the request logging middleware)
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        # Add extra fields passed via `extra={}`
        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)

        # Add exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


class DevFormatter(logging.Formatter):
    """Human-readable log formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",     # cyan
        "INFO": "\033[32m",      # green
        "WARNING": "\033[33m",   # yellow
        "ERROR": "\033[31m",     # red
        "CRITICAL": "\033[1;31m", # bold red
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        request_id = getattr(record, "request_id", None)
        rid_part = f" [{request_id[:8]}]" if request_id else ""
        
        message = (
            f"{color}{record.levelname:<8}{self.RESET}"
            f"{rid_part} "
            f"{record.name} - {record.getMessage()}"
        )
        
        # Add exception traceback if present
        if record.exc_info and record.exc_info[0] is not None:
            message += "\n" + self.formatException(record.exc_info)
        
        return message


def setup_logging(*, log_level: str = "INFO", env: str = "production") -> None:
    """
    Configure the root logger and suppress noisy third-party loggers.
    Call once at application startup.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        JSONFormatter() if env == "production" else DevFormatter()
    )

    # Configure root logger
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Suppress noisy third-party loggers
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if level <= logging.DEBUG else logging.WARNING
    )
