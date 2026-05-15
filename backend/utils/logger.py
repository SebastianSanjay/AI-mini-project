import logging
import os
from config import settings

# Ensure log dir exists
log_dir = os.path.join(settings.LOCAL_STORAGE_DIR, "logs")
os.makedirs(log_dir, exist_ok=True)

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    if log_file:
        fh = logging.FileHandler(os.path.join(log_dir, log_file))
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

logger = setup_logger("linguafuse", "linguafuse.log")
