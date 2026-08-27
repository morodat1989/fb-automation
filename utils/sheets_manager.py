import time
import logging
from typing import List, Dict, Any
import gspread
from config import CREDENTIALS_PATH, SPREADSHEET_NAME

logger = logging.getLogger("SheetsManager")

def retry_api_call(max_retries: int = 3, delay: int = 2):
    """
    Decorator tự động retry khi gặp sự cố kết nối hoặc Quota Limit Google API.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except gspread.exceptions.APIError as e:
                    logger.warning(f"Google Sheets API Error (Lần {attempt}/{max_retries}): {e}")
                    if attempt == max_retries:
                        raise e
                    time.sleep(delay * (2 ** (attempt - 1)))
                except Exception as e:
                    raise e
        return wrapper
    return decorator

class SheetsManager:
    def __init__(self) -> None:
        if not CREDENTIALS_PATH.exists():
            logger.error(f"Không tìm thấy file credentials tại: {CREDENTIALS_PATH}")
            raise FileNotFoundError(f"Không tìm thấy file credentials tại {CREDENTIALS_PATH}")

        self.gc = gspread.service_account(filename=str(CREDENTIALS_PATH))
        self.sheet = self.gc.open(SPREADSHEET_NAME).sheet1
        self._ensure_headers()

    @retry_api_call(max_retries=3, delay=2)
    def _ensure_headers(self) -> None:
        headers = ["Thời Gian", "Người Gửi/Nguồn", "Nội Dung Thô", "Tiêu Đề AI", "Giá", "Vị Trí", "Bài Đăng FB", "Trạng Thái Đăng"]
        existing = self.sheet.row_values(1)
        if not existing:
            self.sheet.insert_row(headers, 1)

    @retry_api_call(max_retries=3, delay=2)
    def append_lead(self, timestamp: str, sender: str, raw_msg: str, ai_data: Dict[str, Any]) -> int:
        row = [
            timestamp,
            sender,
            raw_msg,
            ai_data.get("title", ""),
            ai_data.get("price", ""),
            ai_data.get("location", ""),
            ai_data.get("fb_content", ""),
            "Chờ đăng"
        ]
        self.sheet.append_row(row)
        logger.info("Đã ghi thành công bài viết mới vào Google Sheet.")
        return len(self.sheet.get_all_values())

    @retry_api_call(max_retries=3, delay=2)
    def get_pending_posts(self) -> List[Dict[str, Any]]:
        records = self.sheet.get_all_records()
        pending = []
        for idx, rec in enumerate(records, start=2):
            if rec.get("Trạng Thái Đăng") == "Chờ đăng":
                rec["row_index"] = idx
                pending.append(rec)
        return pending

    @retry_api_call(max_retries=3, delay=2)
    def update_post_status(self, row_index: int, status: str = "Đã đăng") -> None:
        # Cột 8 tương ứng với 'Trạng Thái Đăng'
        self.sheet.update_cell(row_index, 8, status)
        logger.info(f"Đã cập nhật trạng thái dòng {row_index} -> '{status}'")