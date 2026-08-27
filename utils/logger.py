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

# Class tương thích ngược cho các file gọi get_logger().info() / .error()
class _LoggerAdapter:
    def info(self, msg, *args, **kwargs):
        log_info(str(msg))
    def warning(self, msg, *args, **kwargs):
        log_warning(str(msg))
    def error(self, msg, *args, **kwargs):
        log_error(str(msg))
    def debug(self, msg, *args, **kwargs):
        log_debug(str(msg))

_global_logger = _LoggerAdapter()

def get_logger(name: str = "FBAutomation"):
    """Trả về đối tượng logger chuẩn tương thích với core/humanizer.py"""
    return _global_logger