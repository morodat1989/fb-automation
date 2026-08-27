import sys
import time
import logging
from playwright.sync_api import sync_playwright

from login_setup import run_login_setup
from core.ai_processor import AIProcessor
from utils.sheets_manager import SheetsManager
from core.zalo_listener import ZaloListener
from core.fb_poster import FBPoster
from config import BROWSER_PROFILE_DIR

logger = logging.getLogger("MainRunner")

def run_auto_pipeline() -> None:
    logger.info("Kích hoạt Luồng Tự Động Trọn Gói (Auto Pipeline)...")
    ai = AIProcessor()
    sheets = SheetsManager()
    listener = ZaloListener(ai_processor=ai, sheets_manager=sheets)
    poster = FBPoster(sheets_manager=sheets)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE_DIR),
            headless=False,
            viewport={'width': 1366, 'height': 768},
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        page = context.new_page()
        page.goto("https://chat.zalo.me", wait_until="domcontentloaded")
        logger.info("[PIPELINE READY] Zalo Web đã sẵn sàng lắng nghe.")

        last_fb_check = 0.0
        fb_interval = 300.0  # Chu kỳ 5 phút quét Facebook 1 lần

        try:
            while True:
                # 1. Quét tin nhắn Zalo liên tục
                listener.check_new_messages(page)

                # 2. Định kỳ kiểm tra và đăng bài chờ trên Google Sheet
                now = time.time()
                if now - last_fb_check > fb_interval:
                    logger.info("[PIPELINE] Bắt đầu chu kỳ quét Google Sheet đăng FB...")
                    poster.post_pending_items(headless=False)
                    last_fb_check = now

                page.wait_for_timeout(5000)
        except KeyboardInterrupt:
            logger.info("Đã nhận tín hiệu dừng từ người dùng.")
        finally:
            context.close()

def main() -> None:
    print("==================================================")
    print("      HỆ THỐNG TỰ ĐỘNG HÓA ZALO -> FB POSTER      ")
    print("==================================================")
    print("1. [Setup] Đăng nhập & Tạo Session (Zalo/Facebook)")
    print("2. [Run] Lắng nghe Zalo -> AI Xử lý -> Lưu Sheet")
    print("3. [Run] Đọc Sheet -> Đăng bài tự động lên Facebook")
    print("4. [Auto] Luồng tự động trọn gói (Lắng nghe & Auto Post)")
    print("5. Thoát")
    print("==================================================")

    choice = input("Nhập lựa chọn của bạn (1-5): ").strip()

    if choice == '1':
        run_login_setup()
    elif choice == '2':
        ai = AIProcessor()
        sheets = SheetsManager()
        listener = ZaloListener(ai_processor=ai, sheets_manager=sheets)
        listener.start_listening(headless=False)
    elif choice == '3':
        sheets = SheetsManager()
        poster = FBPoster(sheets_manager=sheets)
        group_url = input("Nhập URL Nhóm FB (Để trống nếu đăng trang cá nhân): ").strip()
        poster.post_pending_items(group_url=group_url if group_url else None, headless=False)
    elif choice == '4':
        run_auto_pipeline()
    elif choice == '5':
        logger.info("Thoát chương trình.")
        sys.exit(0)
    else:
        print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()