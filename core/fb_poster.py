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
            print("[FB POSTER] Không có bài viết nào ở trạng thái 'Chờ đăng'.")
            return

        print(f"[FB POSTER] Tìm thấy {len(pending_list)} bài chờ đăng.")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_PROFILE_DIR),
                headless=headless,
                viewport={'width': 1366, 'height': 768},
                args=["--no-sandbox", "--disable-notifications", "--disable-blink-features=AutomationControlled"]
            )
            page = context.new_page()

            target_url = group_url if group_url else "https://www.facebook.com"
            page.goto(target_url, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            for item in pending_list:
                content = item.get("Bài Đăng FB")
                row_idx = item.get("row_index")

                if not content:
                    continue

                try:
                    print(f"[FB POSTER] Đang đăng bài cho dòng {row_idx}...")

                    # Các selector dự phòng để nhấp vào ô "Tạo bài viết"
                    create_post_selectors = [
                        "div[role='button']:has-text('Bạn đang nghĩ gì')",
                        "div[role='button']:has-text('What')",
                        "div[role='button']:has-text('Tạo bài viết')",
                        "span:has-text('Bạn đang nghĩ gì')",
                        "div[aria-label='Tạo bài viết']"
                    ]

                    clicked = False
                    for sel in create_post_selectors:
                        if page.is_visible(sel):
                            page.click(sel)
                            clicked = True
                            break

                    if not clicked:
                        print(f"[FB POSTER ERROR] Không tìm thấy ô tạo bài viết ở dòng {row_idx}")
                        continue

                    page.wait_for_timeout(3000)

                    # Điền nội dung
                    textbox_selector = "div[role='textbox'][contenteditable='true']"
                    page.wait_for_selector(textbox_selector, timeout=10000)
                    page.fill(textbox_selector, content)
                    page.wait_for_timeout(2000)

                    # Các selector dự phòng cho nút "Đăng"
                    submit_selectors = [
                        "div[aria-label='Đăng']",
                        "div[aria-label='Post']",
                        "div[role='button']:has-text('Đăng')",
                        "div[role='button']:has-text('Post')"
                    ]

                    submitted = False
                    for s_sel in submit_selectors:
                        if page.is_visible(s_sel):
                            page.click(s_sel)
                            submitted = True
                            break

                    if submitted:
                        page.wait_for_timeout(7000)
                        self.sheets.update_post_status(row_idx, "Đã đăng")
                        print(f"[FB POSTER] => Đăng bài dòng {row_idx} thành công!")
                    else:
                        print(f"[FB POSTER ERROR] Không tìm thấy nút Đăng cho dòng {row_idx}")

                except Exception as e:
                    print(f"[FB POSTER ERROR] Lỗi đăng bài dòng {row_idx}: {e}")
                    self.sheets.update_post_status(row_idx, f"Lỗi: {str(e)[:30]}")

            context.close()