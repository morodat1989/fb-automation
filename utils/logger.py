import sys
from datetime import datetime

def _get_time():
    return datetime.now().strftime("%H:%M:%S")

def log_info(message: str):
    print(f"[{_get_time()}] [INFO] {message}")

def log_warning(message: str):
    print(f"[{_get_time()}] [WARNING] ⚠️ {message}")

def log_error(message: str):
    print(f"[{_get_time()}] [ERROR] ❌ {message}", file=sys.stderr)

def log_success(message: str):
    print(f"[{_get_time()}] [SUCCESS] ✅ {message}")

def log_debug(message: str):
    print(f"[{_get_time()}] [DEBUG] {message}")