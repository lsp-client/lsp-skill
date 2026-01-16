import sys

from loguru import logger

from lsp_cli.settings import settings


def setup_debug(debug: bool) -> None:
    if debug:
        settings.debug = True
        logger.remove()
        logger.add(sys.stderr, level=settings.effective_log_level)
