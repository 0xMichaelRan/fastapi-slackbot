import logging


def setup_logging() -> logging.Logger:
    """Configure and setup logging for the application"""

    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Get the main logger
    logger = logging.getLogger(__name__)

    # Configure module-specific logging levels
    LOGGING_CONFIG = {
        "pika": logging.WARNING,
        "pika.heartbeat": logging.INFO,
        "pika.adapters": logging.WARNING,
        "pika.connection": logging.INFO,
        "pika.channel": logging.INFO,
        "broker": logging.INFO,
    }

    # Apply logging configuration
    for logger_name, level in LOGGING_CONFIG.items():
        logging.getLogger(logger_name).setLevel(level)

    return logger
