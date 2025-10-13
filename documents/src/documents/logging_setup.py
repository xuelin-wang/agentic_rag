"""Configuration helpers for structlog-based logging."""

from __future__ import annotations

import logging
import sys
from typing import Final

import structlog

_CONFIGURED: Final = {"logging": True}


def configure_logging() -> None:
    """Configure structlog and standard logging for JSON output."""

    if _CONFIGURED["logging"]:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        stream=sys.stdout,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    _CONFIGURED["logging"] = True
