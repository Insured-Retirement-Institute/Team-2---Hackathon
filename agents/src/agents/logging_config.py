"""
Centralized logging configuration for all agents.

Import this module at the top of any agents module to enable consistent logging.
The log level is controlled by the LOG_LEVEL environment variable (default: INFO).

Usage:
    from agents.logging_config import get_logger
    logger = get_logger(__name__)
    logger.debug("Debug message")
    logger.info("Info message")
"""

from __future__ import annotations

import logging
import os
import sys

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
    force=True,
)

if LOG_LEVEL == "DEBUG":
    logging.getLogger("strands").setLevel(logging.DEBUG)
    logging.getLogger("botocore").setLevel(logging.INFO)
    logging.getLogger("boto3").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name. Use __name__ for module-level loggers."""
    return logging.getLogger(name)
