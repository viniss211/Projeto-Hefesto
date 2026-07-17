"""Configuração centralizada dos logs."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    *,
    level: str = "INFO",
    log_directory: str | Path = "logs",
) -> None:
    """Configura logs de arquivo e console."""

    directory = Path(log_directory)
    directory.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("assistente_local")

    if logger.handlers:
        return

    numeric_level = getattr(
        logging,
        level.upper(),
        logging.INFO,
    )

    logger.setLevel(numeric_level)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        directory / "hefesto.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)