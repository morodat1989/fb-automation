import logging
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from config import BROWSER_PROFILE_DIR
from utils.sheets_manager import SheetsManager

logger = logging.getLogger("FBPoster")

class FBPoster:
    def __init__(self, sheets_manager: SheetsManager) -> None:
        self.sheets = sheets_manager

    def post_pending_items(self, group_url: Optional[str] = None, headless: bool = False) -> None:
        pending_list = self.sheets.get_pending_posts()
        if not pending_list:
            logger.info("[FB POSTER] Không có bài viết nào đang ở trạng thái 'Chờ đăng'.")
            return

        logger.info(f"[FB POSTER] Phát hiện {len(pending_list)} bài viết cần đăng.")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_PROFILE_DIR),
                channel="chrome",
                headless=headless,
                viewport={'width': 1366, 'height': 768},
                args=[
                    "--no-sandbox",
                    "--disable-notifications",
                    "--disable-blink-features=AutomationControlled",
                    "--enable-gpu",
                    "--disable-dev-shm-usage",
                    "--remote-debugging-port=9222"
                ]
            )
            page = context.new_page()
            target_url = group_url if group_url else "https://www.facebook.com"

            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(5000)
            except PlaywrightTimeoutError:
                logger.error(f"[FB POSTER] Timeout khi tải URL Facebook: {target_url}")
                context.close()
                return

            for item in pending_list:
                content = item.get("Bài Đăng FB")
                row_idx = item.get("row_index")
                if not content or not row_idx:
                    continue

                self._process_single_post(page, row_idx, content)

            context.close()

    def _process_single_post(self, page, row_idx: int, content: str) -> None:
        try:
            logger.info(f"[FB POSTER] Tiến hành đăng bài cho dòng {row_idx}...")

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
                logger.error(f"[FB POSTER] Dòng {row_idx}: Không tìm thấy khung tạo bài viết.")
                self.sheets.update_post_status(row_idx, "Lỗi: Không thấy nút tạo bài")
                return

            page.wait_for_timeout(3000)
            textbox_selector = "div[role='textbox'][contenteditable='true']"
            page.wait_for_selector(textbox_selector, timeout=10000)
            page.fill(textbox_selector, content)
            page.wait_for_timeout(2000)

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
                logger.info(f"[FB POSTER] Đăng thành công bài viết dòng {row_idx}!")
            else:
                logger.error(f"[FB POSTER] Dòng {row_idx}: Không tìm thấy nút Đăng.")
                self.sheets.update_post_status(row_idx, "Lỗi: Không thấy nút Đăng")

        except Exception as e:
            logger.error(f"[FB POSTER] Lỗi xử lý dòng {row_idx}: {e}", exc_info=True)
            self.sheets.update_post_status(row_idx, f"Lỗi: {str(e)[:25]}")