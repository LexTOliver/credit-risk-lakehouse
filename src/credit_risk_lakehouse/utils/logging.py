from __future__ import annotations

import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=False,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)
