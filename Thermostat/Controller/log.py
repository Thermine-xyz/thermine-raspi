import logging
import os
from datetime import datetime

class Logger:
    
    # log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    def __init__(self, log_path="", log_file="server.log", log_level=logging.INFO):
        log_dir = os.path.join(log_path, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_path = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}_{log_file}")

        self.logger = logging.getLogger("WebServiceLogger")
        self.logger.setLevel(log_level)

        if self.logger.handlers:
            self.logger.handlers.clear()

        log_format = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(log_format)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger