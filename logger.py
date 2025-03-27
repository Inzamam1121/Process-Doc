import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create Logs directory if it doesn't exist
log_dir = "Logs"
os.makedirs(log_dir, exist_ok=True)

# Get today's date for log file naming
today_date = datetime.now().strftime('%Y-%m-%d')
log_filename = f"log_{today_date}.log"
log_filepath = os.path.join(log_dir, log_filename)

file_handler = RotatingFileHandler(
    log_filepath, maxBytes=10 * 1024 * 1024, backupCount=10 
)

# Define log format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR) 
logger.addHandler(file_handler)
