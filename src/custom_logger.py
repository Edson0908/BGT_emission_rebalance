import logging
from colorama import Fore, Style
import os

class CustomFormatter(logging.Formatter):
    """
    Custom Formatter to add colors to log messages based on their severity level.
    """
    LOG_COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.LOG_COLORS.get(record.levelno, "")
        reset_color = Style.RESET_ALL
        record.msg = f"{log_color}{record.msg}{reset_color}"
        return super().format(record)
    
    
os.makedirs('logs', exist_ok=True)
logger = logging.getLogger("GlobalLogger")
logger.setLevel(logging.DEBUG)

logger.handlers = []
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

file_handler = logging.FileHandler('logs/BGTAllocation.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)  # 设置文件处理程序的日志级别
logger.addHandler(file_handler)

def get_logger() -> logging.Logger:
    return logger
