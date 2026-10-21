from __future__ import annotations

import logging


def setup_logging(level_name: str = "INFO") -> None:
    """Set up logging configuration."""
    level = getattr(logging, level_name.upper())

    if not isinstance(level, int):
        raise ValueError(f"Invalid log level: {level_name}")

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=False,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)
