import logging
from playwright.sync_api import sync_playwright
from config import BROWSER_PROFILE_DIR

logger = logging.getLogger("LoginSetup")

def run_login_setup() -> None:
    logger.info("Đang khởi động Google Chrome Setup Session...")
    print("\n==================================================")
    print(" HƯỚNG DẪN SETUP BẢO MẬT & SESSION:")
    print(" 1. Trên tab Facebook: Nhập mã 2FA / Xác minh bảo mật (nếu có).")
    print(" 2. Trên tab Zalo: Mở điện thoại bấm 'Đồng bộ tin nhắn'.")
    print(" 3. Khi cả 2 trang đã vào giao diện chính, quay lại đây nhấn ENTER.")
    print("==================================================\n")

    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_PROFILE_DIR),
                channel="chrome",
                headless=False,
                viewport={'width': 1366, 'height': 768},
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--remote-debugging-port=9222"
                ]
            )

            page_zalo = context.new_page()
            page_zalo.goto("https://chat.zalo.me", wait_until="networkidle")

            page_fb = context.new_page()
            page_fb.goto("https://www.facebook.com", wait_until="networkidle")

            input("--> Nhấn ENTER sau khi bạn đã vượt qua 2FA FB và đồng bộ Zalo thành công...")
            logger.info("Đã lưu Session thành công vào 'browser_profile/'.")
            context.close()
        except Exception as e:
            logger.error(f"Lỗi khi mở Chrome: {e}")
            print("\n[LƯU Ý] Hãy đóng tất cả cửa sổ Chrome đang mở trên máy rồi thử lại!")

if __name__ == "__main__":
    run_login_setup()