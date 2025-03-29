import logging
import os
from datetime import datetime
from config import LOGS_DIR

logger = None

def setup_logging():
    global logger
    if logger is not None:
        return logger

    logger = logging.getLogger("CallAnalytics")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        logger.handlers.clear()

    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    log_filename = os.path.join(LOGS_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(log_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger