"""Simple logging setup used across the app."""
import logging
import sys
from src import config


def get_logger(name: str = "resume_parser") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    file_handler = logging.FileHandler(config.LOGS_DIR / "app.log")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger


logger = get_logger()
