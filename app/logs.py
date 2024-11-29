"""Setting up logging."""
import logging
import logging.handlers
from pathlib import Path
from typing import Sequence

from asgi_correlation_id import CorrelationIdFilter
from rich.console import Console
from rich.logging import RichHandler

from app.settings import settings

logger = logging.getLogger(__name__)


def setup_logging(
        log_location: Path,
        log_level: str,
        packages_to_suppress: Sequence[str] | None = None
) -> None:
    """Sets up the different loggers."""
    # Changing fastapi module log level
    logging.getLogger('fastapi').setLevel(logging.ERROR)

    # Setting up
    cid_filter = CorrelationIdFilter(uuid_length=8)

    # Setup FileHandler
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=log_location, encoding='utf-8', when='W0')
    file_handler.addFilter(cid_filter)
    file_handler.setLevel(settings.LOG_LEVEL)

    # Config
    logging.basicConfig(level=log_level,
                        format='%(asctime)s [%(correlation_id)s] [%(name)s:%(lineno)d] %(levelname)s %(name)s:%(lineno)d %(message)s',
                        handlers=[
                            file_handler,
                            RichHandler(enable_link_path=False, console=Console(width=225))
                        ])

    if not packages_to_suppress:
        packages_to_suppress = ['urllib3', 'suds', 'google.auth.transport.requests', 'gspread_dataframe', 'httpx',
                                'httpcore', 'asyncio', 'tzlocal']
    for package in packages_to_suppress:
        logging.getLogger(package).setLevel(logging.CRITICAL)


async def startup_event():
    logger.info('API started')


async def shutdown_event():
    logger.info('API closed')
