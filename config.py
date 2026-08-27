import os
from pathlib import Path
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Đường dẫn đường dẫn tài khoản Google Sheets
CREDENTIALS_PATH = BASE_DIR / "key" / "credentials.json"
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "BDS_Auto_Post")

# Đường dẫn lưu Trình duyệt (Profile cố định)
BROWSER_PROFILE_DIR = BASE_DIR / "browser_profile"
ZALO_SESSION_DIR = BASE_DIR / "zalo_session"
FB_SESSION_DIR = BASE_DIR / "fb_session"

# Đảm bảo các thư mục cần thiết tồn tại
BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
ZALO_SESSION_DIR.mkdir(parents=True, exist_ok=True)
FB_SESSION_DIR.mkdir(parents=True, exist_ok=True)