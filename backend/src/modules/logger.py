"""
Logging related functions
"""
import logging
from fastapi import Request

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a console handler and set the log level to DEBUG
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)


def get_logger():
    """
    Logging return function for hiding from user
    """
    return logger


def log_request(request: Request, request_logger: logging.Logger = get_logger()):
    """
    Logging related functions
    """
    request_logger.info(f"Endpoint: {request.url.path}, Method: {request.method}")
