import os
import logging
from datetime import datetime

from .utils import db, time, tools
from .server import Server
from . import PacketClasses

# Set root file location as system variable
ROOT = os.path.dirname(__file__)
os.environ["CIM_ROOT"] = ROOT

t = datetime.now().strftime("%Y-%m-%d-%h-%M-%S.%f")

# Create logs folder if it doesn't exist
if not os.path.isdir(ROOT + "/logs"):
    os.mkdir(ROOT + "/logs")

# Load the logging config
logger_config = tools.load_config("logging.json")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter('%(asctime)s - %(levelname)8s [%(name)s] : %(message)s')

# Create a file handler for the logging
file_handler = logging.FileHandler(filename=f"{ROOT}/logs/{t}", encoding="utf-8", mode="w")
file_handler.setFormatter(log_format)

# Create a stream handler to output logging to console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.info("Logger Initialised")
