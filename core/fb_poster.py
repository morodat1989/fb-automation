import time
from playwright.sync_api import sync_playwright
from config import BROWSER_PROFILE_DIR
from utils.sheets_manager import SheetsManager

class FBPoster:
    def __init__(self, sheets_manager: SheetsManager):
        self.sheets = sheets_manager

    def post_pending_items(self, group_url: str = None, headless=False):
        pending_list = self.sheets.get_pending_posts()
        if not pending_list:
            print("[FB POSTER] Không có bài viết nào chờ đăng.")
            return

        print(f"[FB POSTER] Tìm thấy {len(pending_list)} bài chờ đăng.")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_PROFILE_DIR),
                headless=headless,
                args=["--no-sandbox", "--disable-notifications"]
            )
            page = context.new_page()

            target_url = group_url if group_url else "https://www.facebook.com"
            page.goto(target_url)
            page.wait_for_timeout(5000)

            for item in pending_list:
                content = item.get("Bài Đăng FB")
                row_idx = item.get("row_index")
                
                if not content:
                    continue

                try:
                    print(f"[FB POSTER] Đang đăng bài cho dòng {row_idx}...")
                    # Click vào ô tạo bài viết Facebook
                    page.click("text=Bạn đang nghĩ gì?")
                    page.wait_for_timeout(2000)
                    
                    # Điền nội dung bài viết
                    page.fill("div[role='textbox']", content)
                    page.wait_for_timeout(2000)
                    
                    # Click nút Đăng
                    page.click("div[aria-label='Đăng']")
                    page.wait_for_timeout(5000)

                    # Cập nhật trạng thái trên Google Sheet
                    self.sheets.update_post_status(row_idx, "Đã đăng")
                    print(f"[FB POSTER] Đăng bài dòng {row_idx} thành công!")

                except Exception as e:
                    print(f"[FB POSTER ERROR] Lỗi đăng bài dòng {row_idx}: {e}")
                    self.sheets.update_post_status(row_idx, f"Lỗi: {str(e)[:30]}")

            context.close()