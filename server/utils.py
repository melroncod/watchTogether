import logging
from logging import Logger

def get_logger(name: str = __name__) -> Logger:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO
    )
    return logging.getLogger(name)
