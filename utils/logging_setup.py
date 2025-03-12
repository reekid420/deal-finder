import os
import sys
from pathlib import Path
from loguru import logger
from utils.config import LOGGING

# Define paths at the module level so they can be imported
SCREENSHOT_PATH = str(Path("logs/screenshots"))
HTML_PATH = str(Path("logs"))

def setup_logging():
    """
    Set up logging with Loguru to:
    1. Log all messages to a main log file
    2. Log only errors and warnings to a separate error log file
    3. Keep console output for debugging
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create screenshots directory if it doesn't exist
    screenshots_dir = Path(SCREENSHOT_PATH)
    screenshots_dir.mkdir(exist_ok=True)
    
    # Clear default loguru handler
    logger.remove()
    
    # Get configuration from LOGGING dict
    log_level = LOGGING.get("log_level", "INFO")
    log_format = LOGGING.get("log_format", "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")
    max_size = LOGGING.get("max_log_size", 10485760)  # 10MB default
    backup_count = LOGGING.get("backup_count", 5)
    
    # Console handler for interactive use (INFO and above)
    logger.add(
        sys.stderr, 
        format=log_format, 
        level=log_level,
        colorize=True,
        backtrace=True,  # Include backtrace for better error reporting
        diagnose=True    # Include variables in tracebacks
    )
    
    # Main log file - all levels (default INFO and above)
    logger.add(
        "logs/crawler.log",
        format=log_format,
        level=log_level,
        rotation=max_size,
        compression="zip",
        retention=backup_count,
        enqueue=True,
        backtrace=True,  # Include backtrace for better error reporting
        diagnose=True    # Include variables in tracebacks
    )
    
    # Error log file - only ERROR and WARNING levels
    logger.add(
        "logs/errors.log",
        format=log_format,
        level="WARNING",  # Capture WARNING and ERROR
        rotation=max_size,
        compression="zip",
        retention=backup_count,
        enqueue=True,
        backtrace=True,  # Include backtrace for better error reporting
        diagnose=True,   # Include variables in tracebacks
        filter=lambda record: record["level"].name in ["WARNING", "ERROR", "CRITICAL"]
    )
    
    # Configure the standard logging library to use loguru
    # This ensures existing logging calls are captured by loguru
    import logging
    
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            # Find caller from where the logged message originated
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    # Setup the root logging handler to use loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Register exception handler for uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions by logging them with Loguru"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log KeyboardInterrupt (Ctrl+C)
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).error("Uncaught exception:")
    
    # Set the excepthook to use our handler
    sys.excepthook = handle_exception
    
    logger.info(f"Logging system initialized with main log: logs/crawler.log and error log: logs/errors.log")
    logger.info(f"Screenshots will be saved to: {SCREENSHOT_PATH}")
    logger.info(f"HTML debug files will be saved to: {HTML_PATH}")
    return logger 