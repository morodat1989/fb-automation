import logging
from playwright.sync_api import sync_playwright
from config import BROWSER_PROFILE_DIR

logger = logging.getLogger("LoginSetup")

def run_login_setup() -> None:
    """
    Mở trình duyệt để người dùng đăng nhập tài khoản Zalo và Facebook thủ công.
    Session và Cookies sẽ được lưu trữ persistent tại folder browser_profile.
    """
    logger.info("Đang khởi động trình duyệt Setup Session...")
    print("\n==================================================")
    print(" HƯỚNG DẪN SETUP BẢO MẬT & SESSION:")
    print(" 1. Trình duyệt Chrome sẽ mở ra 2 tab (Zalo & Facebook).")
    print(" 2. Hãy tiến hành đăng nhập hoàn tất tài khoản của bạn.")
    print(" 3. Sau khi hoàn tất đăng nhập, hãy quay lại Terminal này và nhấn ENTER.")
    print("==================================================\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE_DIR),
            headless=False,
            viewport={'width': 1366, 'height': 768},
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )

        page_zalo = context.new_page()
        page_zalo.goto("https://chat.zalo.me", wait_until="domcontentloaded")

        page_fb = context.new_page()
        page_fb.goto("https://www.facebook.com", wait_until="domcontentloaded")

        input("--> Nhấn ENTER sau khi bạn đã đăng nhập thành công cả Zalo và Facebook...")
        logger.info("Đã lưu Session thành công vào 'browser_profile/'.")
        context.close()

if __name__ == "__main__":
    run_login_setup()