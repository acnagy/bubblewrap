import logging

import coloredlogs


def init_logger():
    level = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)

    console = logging.StreamHandler()
    console.setLevel(level)
    logger.addHandler(console)

    log_format = "%(asctime)s [%(levelname)s] - %(message)s"
    coloredlogs.install(level="INFO", logger=logger, fmt=log_format)

    return logger
