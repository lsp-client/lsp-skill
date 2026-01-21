import logging
import sys

from loguru import logger

from lsp_cli.state import env_state


def setup_logging() -> None:
    """Configure application logging with loguru.

    Only outputs to console (stderr).
    """

    logger.remove()
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=True,
        backtrace=env_state.debug,
        diagnose=env_state.debug,
    )
