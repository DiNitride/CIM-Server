import os
import logging
from datetime import datetime

# Import root file first to set server root in system enviroment
# This file MUST be imported first to ensure it is executed first
# as other files imported later may rely on the existence of the server root in
# the system enviroment
from . import root

from .server import Server
from .user import User
from .token_generator import generate_session_token
from .packet_factory import PacketFactory
from . import packets
from . import utils


# Get current date and time for the log file
t = datetime.now().strftime("%Y-%m-%d-%h-%M-%S.%f")

# Check if the log folder exists, as it won't initally
# Otherwise the server will crash upon trying to save the log
if not os.path.isdir(os.getenv("CIM_ROOT") + "/logs"):
    os.mkdir(os.getenv("CIM_ROOT") + "/logs")

# Get the logger
# __name__ refers to the current module
# In this case, it is CIM, as we are in the init.py file of the CIM folder (Seen as a package by Python)
# Logging settings flow down modules in the package, so for example, calling __name__ within the server.py
# file, would return CIM.server
# Because we are defining the logging settings for CIM, the top level, they also then flow down to CIM.server
# This means logging can be defined once for the whole server
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# NOTE: This logging format only logs to a file, to keep sydout clear if the server is imported into another
# launch (run.py) file. This is to allow flexibility for the admin. Settings to log to the console as
# contained inside the launcher

# How to format the log file
log_format = logging.Formatter('%(asctime)s - %(levelname)8s [%(name)s] : %(message)s')

# Log file handler
file_handler = logging.FileHandler(filename=f"{os.getenv('CIM_ROOT')}/logs/{t}.log", encoding="utf-8", mode="w")
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

logger.info("Logger Initialised")
logger.info(f"Server Root set as {os.getenv('CIM_ROOT')}")
