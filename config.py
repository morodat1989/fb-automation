import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Base Directory definition
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Environment & API Configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "BDS_Auto_Post")

# File Paths
CREDENTIALS_PATH = BASE_DIR / "key" / "credentials.json"
BROWSER_PROFILE_DIR = BASE_DIR / "browser_profile"
STATE_FILE_PATH = BASE_DIR / "processed_hashes.json"
LOG_FILE_PATH = BASE_DIR / "app.log"

# Directories initialization
BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)

# Centralized Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Config")
logger.info("Configuration loaded successfully.")