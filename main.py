import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Create logs directories
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
screenshot_dir = Path("logs/screenshots")
screenshot_dir.mkdir(exist_ok=True)

# Load environment variables first
load_dotenv()

# Set up early basic logging before importing other modules
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/startup_errors.log'),
        logging.StreamHandler()
    ]
)

try:
    # Now set up our proper logging system
    from utils.logging_setup import setup_logging
    logger = setup_logging()
    
    # Safe to import other dependencies now
    import subprocess
    
    def check_environment():
        """Check if all required environment variables are set"""
        required_vars = ["GEMINI_API_KEY"]
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            print(f"Error: Missing required environment variables: {', '.join(missing)}")
            print("Please create a .env file with these variables.")
            return False
        
        logger.info("Environment check passed")
        return True

    def run_app():
        """Launch the Streamlit app"""
        logger.info("Starting Streamlit application")
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", "ui/app.py"])
        except Exception as e:
            logger.error(f"Error starting Streamlit app: {e}")
            raise

    if __name__ == "__main__":
        logger.info("Application starting")
        if check_environment():
            run_app()
        else:
            logger.error("Application exiting due to missing environment variables")
            sys.exit(1)
            
except Exception as e:
    logging.error(f"Error during application startup: {e}", exc_info=True)
    sys.exit(1) 