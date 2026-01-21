from __future__ import annotations

from pathlib import Path

from loguru import logger

from lsp_cli.utils.logging import extra_filter


def setup_manager_logging(log_file: Path) -> None:
    """Setup loguru for manager.

    Args:
        log_file: Path to write manager log to.
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        log_file,
        filter=extra_filter("client_id", exclude=True),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
    )
