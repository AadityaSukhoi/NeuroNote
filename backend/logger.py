"""
NeuroNote Logger
Author: Aaditya Ranjan Moitra
Description:
    Centralized logging setup for NeuroNote backend.
    Uses Python's built-in logging with rotating file handler.
"""

import logging
from logging.handlers import RotatingFileHandler
import os

# -------------------- Create Logs Directory --------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# -------------------- Logger Setup --------------------
logger = logging.getLogger("neuronote")
logger.setLevel(logging.INFO) 

# Rotating file handler: max 5MB per file, keep last 5 files
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5)
file_formatter = logging.Formatter(
    "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
file_handler.setFormatter(file_formatter)

# Console handler for dev environment
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
console_handler.setFormatter(console_formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# -------------------- Convenience Functions --------------------
def log_info(message: str):
    logger.info(message)

def log_debug(message: str):
    logger.debug(message)

def log_warning(message: str):
    logger.warning(message)

def log_error(message: str):
    logger.error(message)
