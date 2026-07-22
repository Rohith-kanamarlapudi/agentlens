from __future__ import annotations

import logging
import os


def get_logger(name: str) -> logging.Logger:
    """
    Return a shared logger configured for AgentLens.
    """

    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()

        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s: %(message)s"
            )
        )

        logger.addHandler(handler)

    logger.setLevel(
        os.environ.get(
            "AGENTLENS_LOG_LEVEL",
            "INFO",
        )
    )

    return logger