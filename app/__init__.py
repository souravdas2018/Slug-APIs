import logging, os
from logging.handlers import RotatingFileHandler

# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Set log file path
log_file_path = os.path.join('logs/app.log')
# Set up a rotating file handler
handler = RotatingFileHandler(
    log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3  # Rotate after 5 MB
)

# Set up logging configuration with date and time
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("Starting URL Shortener Service")

