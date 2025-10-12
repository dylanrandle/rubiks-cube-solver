import logging
import os

logging.basicConfig(
    format="[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s",
    level=os.environ.get("LOG_LEVEL", logging.INFO),
    datefmt="%Y-%m-%d %H:%M:%S",
)
