# -*- coding: utf-8 -*-
"""Logging configuration for the application."""

import logging

LOG_FORMAT = "%(asctime)s %(filename)s:%(lineno)d %(funcName)s %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"


def configure_logging():
    """Configure application logging once for console output."""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        force=True,
    )
