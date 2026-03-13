import logging
import json


class CustomJsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = super().format(record)
        return json.dumps(
            {
                "log": log_entry,
                "level": record.levelname,
                "time": self.formatTime(record),
                "message": record.getMessage(),
            }
        )


# Configure logging
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

# Create a file handler that logs debug and higher level messages
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

# Create JSON formatter
formatter = CustomJsonFormatter()
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Example log messages
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
