import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create Logs directory if it doesn't exist
log_dir = "Logs"
os.makedirs(log_dir, exist_ok=True)

# Get today's date for log file naming
today_date = datetime.now().strftime('%Y-%m-%d')

# General Log File
general_log_filepath = os.path.join(log_dir, f"log_{today_date}.log")
general_handler = RotatingFileHandler(
    general_log_filepath, maxBytes=10 * 1024 * 1024, backupCount=10   
)

# Directory Processing Log File
dir_log_filepath = os.path.join(log_dir, "processeddir.log")
dir_handler = RotatingFileHandler(
    dir_log_filepath, maxBytes=10 * 1024 * 1024, backupCount=10  
)

# Define log format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Apply formatters
general_handler.setFormatter(formatter)
dir_handler.setFormatter(formatter)

# Ensure handlers capture both INFO and ERROR logs
general_handler.setLevel(logging.INFO)
dir_handler.setLevel(logging.INFO)

# Create loggers and allow both INFO and ERROR
general_logger = logging.getLogger("general_logger")
general_logger.setLevel(logging.INFO)
general_logger.addHandler(general_handler)

dir_logger = logging.getLogger("dir_logger")
dir_logger.setLevel(logging.INFO) 
dir_logger.addHandler(dir_handler)

# Prevent duplicate logs
general_logger.propagate = False
dir_logger.propagate = False
