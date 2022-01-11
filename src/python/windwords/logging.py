import logging

from windwords import constants


def get_logger(name, level=logging.INFO):
    """ Returns a logger initialised to generate output to the console.

    Args:
        name (str): The logger name
        level (int): The default logger level. Defaults to logging.INFO.
    Returns:
        logging.Logger: The logger instance
    """
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    logger.setLevel(level)
    handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


LOGGER = get_logger(constants.APPLICATION_NAME, level=logging.DEBUG)
