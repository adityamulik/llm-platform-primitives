"""Shared logging setup.

Each service calls :func:`setup_logging` once at startup to send its logs to a
dedicated flat file under the repo-root ``logs/`` directory (git-ignored), while
still echoing to the console. This keeps per-service logs isolated and easy to
``tail -f``.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# logs/ lives at the repo root: observability/logging/__init__.py -> repo root is
# two parents up.
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"

_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

# Track services already configured so repeated calls (e.g. uvicorn reloads) do
# not stack duplicate handlers.
_configured: set[str] = set()


def setup_logging(
    service: str,
    *,
    level: int = logging.INFO,
    console: bool = True,
) -> Path:
    """Route the root logger to ``logs/<service>.log`` (and the console).

    Returns the path of the log file so callers can surface it on startup.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"{service}.log"

    root = logging.getLogger()
    root.setLevel(level)

    if service not in _configured:
        formatter = logging.Formatter(_FORMAT)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

        if console:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            root.addHandler(stream_handler)

        _configured.add(service)

    return log_file
