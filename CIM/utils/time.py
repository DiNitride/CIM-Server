from datetime import datetime
import dateparser
import logging

logger = logging.getLogger(__name__)

# Methods to return the current time in various format

def pretty_time():
    # logger.debug("Returning current datetime in pretty print")
    return datetime.now().strftime("%b/%d/%Y %H:%M:%S")


def now():
    # logger.debug("Returning current datetime in object form")
    return datetime.now()


def iso():
    return datetime.now().isoformat()[:-3]


def log_file_time_format():
    # logger.debug("Returning current datetime in log format")
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")


def timestamp_to_obj(timestamp: str):
    # logger.debug(f"Parsing {timestamp} into datetime object")
    return dateparser.parse(timestamp)
