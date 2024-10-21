import logging
import logging.handlers
from pathlib import Path
from typing import Sequence

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
        log_location: Path,
        log_level: str,
        packages_to_suppress: Sequence[str] | None = None
) -> None:
    """
    Setup logging
    :param log_location: Path to the log file
    :param log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL')
    :param packages_to_suppress: Package names for which to set the log level to WARNING always, defaults to
    ['urllib3', 'suds', 'google.auth.transport.requests', 'gspread_dataframe', 'httpx']
    :return:
    """
    default_fmt = "%(message)s"

    assert log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], f'Invalid log level {log_level}'

    # Create log directory if it doesn't exist
    log_location.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.handlers.TimedRotatingFileHandler(filename=log_location, when='W0')
    file_handler.formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s')

    logging.basicConfig(
        level=log_level,
        format=default_fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            RichHandler(enable_link_path=False, console=Console(width=225)),
            file_handler
        ]
    )

    if not packages_to_suppress:
        packages_to_suppress = ['urllib3', 'suds', 'google.auth.transport.requests', 'gspread_dataframe', 'httpx',
                                'httpcore', 'asyncio']
    for package in packages_to_suppress:
        logging.getLogger(package).setLevel(logging.CRITICAL)
