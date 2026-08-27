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
        # Cấu hình bypass chống nhận diện tự động hóa để Zalo tải ảnh mượt mà
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE_DIR),
            headless=False,
            viewport={'width': 1366, 'height': 768},
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled", # Giúp Zalo không chặn tải ảnh/CDN
                "--start-maximized"
            ]
        )

        if choice in ['1', '3']:
            print("\n[ZALO] Đang mở Zalo Web... Hãy quét mã QR và chờ đồng bộ ảnh.")
            zalo_page = context.new_page()
            zalo_page.goto("https://chat.zalo.me", wait_until="domcontentloaded")
            input("\n>>> Sau khi đã đồng bộ và thấy ảnh hiện đầy đủ trên Zalo, nhấn ENTER...")

        if choice in ['2', '3']:
            print("\n[FACEBOOK] Đang mở Facebook ở Tab mới...")
            fb_page = context.new_page() # Tách riêng tab mới, không đè lên tab Zalo
            fb_page.goto("https://www.facebook.com", wait_until="domcontentloaded")
            input("\n>>> Sau khi đã đăng nhập Facebook xong, nhấn ENTER tại đây...")

        print("\n[SUCCESS] Đã lưu thành công phiên làm việc vào 'browser_profile/'.")
        context.close()

if __name__ == "__main__":
    run_login_setup()