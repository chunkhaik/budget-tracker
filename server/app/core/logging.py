import logging
from logging.config import dictConfig

from app.core.config import get_settings


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}


def configure_logging() -> None:
    settings = get_settings()
    config = LOGGING_CONFIG | {"root": {"level": settings.log_level.upper(), "handlers": ["console"]}}
    dictConfig(config)
    logging.getLogger(__name__).debug("logging configured")
