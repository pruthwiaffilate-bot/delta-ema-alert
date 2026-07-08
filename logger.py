"""Logging setup for delta-ema-alert.

Creates a console handler and rotating file handler with colorized output.
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import os
import colorlog


def get_logger(name: str = "delta_ema") -> logging.Logger:
    """Return configured logger.

    Args:
        name: logger name

    Returns:
        logging.Logger
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    logfile = os.path.join(log_dir, "delta-ema.log")

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ch = colorlog.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    fh = RotatingFileHandler(logfile, maxBytes=10 * 1024 * 1024, backupCount=5)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
