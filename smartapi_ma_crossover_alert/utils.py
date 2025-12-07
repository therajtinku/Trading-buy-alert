import logging
import pytz
from datetime import datetime

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """Returns a configured logger instance."""
    return logging.getLogger(name)

def get_ist_time():
    """Returns current time in IST timezone."""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def format_ist_time(dt=None):
    """Formats a datetime object to string in IST."""
    if dt is None:
        dt = get_ist_time()
    return dt.strftime('%Y-%m-%d %H:%M:%S')
