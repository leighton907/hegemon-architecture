import logging
import os


def get_logger(log_file):

    logger = logging.getLogger("ASTRA_LOG")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s [ASTRA_LOG] %(levelname)s %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
