import os
import logging
from datetime import datetime

# Import root file first to set server root in system envs
from . import root

from .server import Server
from .user import User
from . import PacketClasses, errors
from . import utils

t = datetime.now().strftime("%Y-%m-%d-%h-%M-%S.%f")

if not os.path.isdir(os.getenv("CIM_ROOT") + "/logs"):
    os.mkdir(os.getenv("CIM_ROOT") + "/logs")

logger_config = utils.tools.load_config("logging.json")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter('%(asctime)s - %(levelname)8s [%(name)s] : %(message)s')


file_handler = logging.FileHandler(filename=f"{os.getenv('CIM_ROOT')}/logs/{t}", encoding="utf-8", mode="w")
file_handler.setFormatter(log_format)

# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(log_format)

logger.addHandler(file_handler)
# logger.addHandler(stream_handler)

logger.info("Logger Initialised")
