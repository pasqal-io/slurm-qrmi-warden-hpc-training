import json
import logging
import os

logging.basicConfig(
    level=logging.DEBUG,  # or INFO
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger()

logger.info(json.dumps(dict(os.environ)))
