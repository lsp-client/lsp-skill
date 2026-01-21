from __future__ import annotations

import logging
from pathlib import Path

import structlog

_log_files: dict[str, Path] = {}


def setup_manager_logging(log_file: Path) -> None:
    """Setup structlog for manager.

    Args:
        log_file: Path to write manager log to.
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)
    _log_files["manager"] = log_file

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(
            file=log_file.open("a", encoding="utf-8")
        ),
        cache_logger_on_first_use=False,
    )


def get_client_logger(client_id: str, log_dir: Path) -> structlog.BoundLogger:
    """Get a logger for a specific ManagedClient.

    Each client gets its own log file.

    Args:
        client_id: Unique identifier for the client.
        log_dir: Directory to write client logs to.

    Returns:
        A bound logger with client_id context.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    client_log_file = log_dir / f"{client_id}.log"
    _log_files[client_id] = client_log_file

    logger_factory = structlog.WriteLoggerFactory(
        file=client_log_file.open("a", encoding="utf-8")
    )
    logger = structlog.wrap_logger(
        logger_factory(),
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        cache_logger_on_first_use=False,
    )

    return logger.bind(client_id=client_id)
