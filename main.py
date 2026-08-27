import sys
import time
from login_setup import run_login_setup
from core.ai_processor import AIProcessor
from utils.sheets_manager import SheetsManager
from core.zalo_listener import ZaloListener
from core.fb_poster import FBPoster
from playwright.sync_api import sync_playwright
from config import BROWSER_PROFILE_DIR

def run_auto_pipeline():
    print("\n==================================================")
    print("   KÍCH HOẠT LUỒNG TỰ ĐỘNG ZALO -> AI -> SHEET -> FB   ")
    print("==================================================")
    ai = AIProcessor()
    sheets = SheetsManager()
    listener = ZaloListener(ai_processor=ai, sheets_manager=sheets)
    poster = FBPoster(sheets_manager=sheets)

    print("[AUTO] Đang mở Zalo Web trên trình duyệt...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE_DIR),
            headless=False,
            viewport={'width': 1366, 'height': 768},
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        page = context.new_page()
        page.goto("https://chat.zalo.me", wait_until="domcontentloaded")
        print("[AUTO] Hệ thống đã sẵn sàng. Đang lắng nghe Zalo & đăng FB định kỳ...")

        last_fb_check = 0
        fb_interval = 300  # 5 phút (300 giây) kiểm tra và đăng FB 1 lần

        try:
            while True:
                # 1. Quét tin nhắn Zalo liên tục
                listener.check_new_messages(page)

                # 2. Kiểm tra bài viết chờ đăng FB theo chu kỳ 5 phút
                now = time.time()
                if now - last_fb_check > fb_interval:
                    print("\n[AUTO] Đến chu kỳ quét bài 'Chờ đăng' lên Facebook...")
                    poster.post_pending_items(headless=False)
                    last_fb_check = now

                time.sleep(5)
        except KeyboardInterrupt:
            print("\n[AUTO] Đã dừng luồng tự động.")
        finally:
            context.close()

def main():
    print("==================================================")
    print("      HỆ THỐNG TỰ ĐỘNG HÓA ZALO -> FB POSTER      ")
    print("==================================================")
    print("1. [Setup] Đăng nhập & Tạo Session (Zalo/Facebook)")
    print("2. [Run] Lắng nghe Zalo -> AI Xử lý -> Lưu Sheet")
    print("3. [Run] Đọc Sheet -> Đăng bài tự động lên Facebook")
    print("4. [Auto] Luồng tự động trọn gói (Lắng nghe Zalo & Tự động đăng FB)")
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
        group_url = input("Nhập URL nhóm/Trang FB muốn đăng (để trống nếu đăng Wall cá nhân): ").strip()
        poster.post_pending_items(group_url=group_url if group_url else None, headless=False)

    elif choice == '4':
        run_auto_pipeline()

    elif choice == '5':
        print("Đã thoát chương trình.")
        sys.exit(0)
    else:
        print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()