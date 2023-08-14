import logging
import logging.config
import sys
from functools import wraps
from pathlib import Path
from typing import Any, Dict

LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "class": "logging.Formatter",
            "format": "[%(asctime)s] [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "level": "DEBUG",
        },
        "less_detailed": {
            "class": "logging.Formatter",
            "format": "[%(asctime)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "level": "INFO",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "less_detailed",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path("logs") / "app.log",
            "mode": "a",
            "formatter": "detailed",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 10,
        },
    },
    "root": {"handlers": ["console", "file"], "level": "DEBUG"},
}


def setup_logger(filename: str) -> Dict[str, Any]:
    """Setup logger that writes to console non-debug logs,
    and writes everything to a rotating file"""
    config = LOGGING_CONFIG
    config["handlers"]["file"]["filename"] = str(
        Path("logs").joinpath(f"{filename}.log")
    )

    Path.mkdir(Path("logs"), mode=0o777, exist_ok=True)
    logging.config.dictConfig(config)

    sys.excepthook = log_uncaught_exceptions
    return config


def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def keyboard_interrupt_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            logging.info("Stopped %s execution", func.__name__)

    return wrapper
