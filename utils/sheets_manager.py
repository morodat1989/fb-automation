import gspread
from config import CREDENTIALS_PATH, SPREADSHEET_NAME

class SheetsManager:
    def __init__(self):
        if not CREDENTIALS_PATH.exists():
            raise FileNotFoundError(f"Không tìm thấy file credentials tại {CREDENTIALS_PATH}")
        
        self.gc = gspread.service_account(filename=str(CREDENTIALS_PATH))
        self.sheet = self.gc.open(SPREADSHEET_NAME).sheet1
        self._ensure_headers()

    def _ensure_headers(self):
        headers = ["Thời Gian", "Người Gửi/Nguồn", "Nội Dung Thô", "Tiêu Đề AI", "Giá", "Vị Trí", "Bài Đăng FB", "Trạng Thái Đăng"]
        existing = self.sheet.row_values(1)
        if not existing:
            self.sheet.insert_row(headers, 1)

    def append_lead(self, timestamp: str, sender: str, raw_msg: str, ai_data: dict) -> int:
        """Thêm lead mới vào Google Sheet và trả về dòng vừa thêm"""
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
        print(f"[SHEETS] Đã ghi thành công dữ liệu vào Google Sheet.")
        return len(self.sheet.get_all_values())

    def get_pending_posts(self) -> list:
        """Lấy danh sách các bài đang ở trạng thái 'Chờ đăng'"""
        records = self.sheet.get_all_records()
        pending = []
        for idx, rec in enumerate(records, start=2): # Dòng 1 là Header
            if rec.get("Trạng Thái Đăng") == "Chờ đăng":
                rec["row_index"] = idx
                pending.append(rec)
        return pending

    def update_post_status(self, row_index: int, status: str = "Đã đăng"):
        """Cập nhật trạng thái đăng bài"""
        # Cột H (Cột 8) là Trạng Thái Đăng
        self.sheet.update_cell(row_index, 8, status)
        print(f"[SHEETS] Đã cập nhật dòng {row_index} thành: {status}")

if __name__ == "__main__":
    sm = SheetsManager()
    print("Kết nối Google Sheets thành công!")