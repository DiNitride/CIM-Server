import os
import logging
from datetime import datetime

from .utils import db, time, tools
from .server import Server
from . import PacketClasses

ROOT = os.path.dirname(__file__)
os.environ["CIM_ROOT"] = ROOT

t = datetime.now().strftime("%Y-%m-%d-%h-%M-%S.%f")

if not os.path.isdir(ROOT + "/logs"):
    os.mkdir(ROOT + "/logs")

logger_config = tools.load_config("logging.json")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter('%(asctime)s - %(levelname)8s [%(name)s] : %(message)s')

file_handler = logging.FileHandler(filename=f"{ROOT}/logs/{t}", encoding="utf-8", mode="w")
file_handler.setFormatter(log_format)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)


logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.info("Logger Initialised")
