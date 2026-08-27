import os
import time
from playwright.sync_api import sync_playwright
from config import BROWSER_PROFILE_DIR

def run_login_setup():
    print("==================================================")
    print("   THIẾT LẬP ĐĂNG NHẬP ZALO & FACEBOOK (PERSISTENT)  ")
    print("==================================================")
    print("1. Đăng nhập Zalo Web")
    print("2. Đăng nhập Facebook")
    print("3. Đăng nhập cả hai")
    choice = input("Lựa chọn của bạn (1/2/3): ").strip()

    with sync_playwright() as p:
        # Khởi tạo browser với user_data_dir để giữ trạng thái đăng nhập
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE_DIR),
            headless=False,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-notifications"]
        )
        page = context.new_page()

        if choice in ['1', '3']:
            print("\n[ZALO] Đang mở Zalo Web... Hãy quét mã QR / Đăng nhập.")
            page.goto("https://chat.zalo.me")
            input("Press ENTER sau khi đã đăng nhập thành công Zalo Web...")

        if choice in ['2', '3']:
            print("\n[FACEBOOK] Đang mở Facebook... Hãy đăng nhập tài khoản.")
            page.goto("https://www.facebook.com")
            input("Press ENTER sau khi đã đăng nhập thành công Facebook...")

        print("\n[SUCCESS] Đã lưu thông tin phiên làm việc vào 'browser_profile/'.")
        context.close()

if __name__ == "__main__":
    run_login_setup()