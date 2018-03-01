import logging

import CIM

logger = logging.getLogger("CIM")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)8s [%(name)s] : %(message)s'))
logger.addHandler(stream_handler)


CIM.Server().start()
