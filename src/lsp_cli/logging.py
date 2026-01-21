import logging
import sys
from pathlib import Path

from loguru import logger

from lsp_cli.settings import settings
from lsp_cli.state import state


def setup_logging(
    *,
    log_file: Path | None = None,
    rotation: str = "10 MB",
    retention: str = "1 day",
) -> None:
    """Configure application logging.

    Args:
        log_file: Optional path to write logs to.
        rotation: Log rotation policy.
        retention: Log retention policy.
    """
    logger.remove()

    if not state.debug:
        logging.getLogger("httpx").setLevel(logging.WARNING)

    # Console handler
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=True,
        backtrace=state.debug,
        diagnose=state.debug,
    )

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            rotation=rotation,
            retention=retention,
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            enqueue=True,
            serialize=not state.debug,  # Use JSON in production (non-debug)
            backtrace=True,
            diagnose=True,
        )
