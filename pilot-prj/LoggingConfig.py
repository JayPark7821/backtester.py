from logging.config import dictConfig
from app.config import config, DevConfig


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "SYSTEM"
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "[%(correlation_id)s] %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s %(msecs)03d %(levelname)-8s %(correlation_id)s %(name)s %(lineno)d %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id"],
                },
                "loki": {
                    "class": "loki_logger_handler.loki_logger_handler.LokiLoggerHandler",
                    "url": "localhost:3100/loki/api/v1/push",
                    "labels": {"service": "pilot-prac-" + ("dev" if isinstance(config, DevConfig) else "prod"),
                               "app": "pilot-prac", "env": "dev" if isinstance(config, DevConfig) else "prod"},
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "app.log",
                    "maxBytes": 1024 * 1024 * 5,
                    "encoding": "utf-8",
                    "backupCount": 30,
                    "filters": ["correlation_id"],
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default", "rotating_file", "loki"],
                    "level": "INFO",
                    "propagate": False
                },
                "app": {
                    "handlers": ["default", "rotating_file", "loki"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False
                },
                "odmantic": {
                    "handlers": ["default", "rotating_file", "loki"],
                    "level": "DEBUG",
                    "propagate": False
                },
            },
        }
    )
