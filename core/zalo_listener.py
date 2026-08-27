import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from config import BROWSER_PROFILE_DIR
from core.ai_processor import AIProcessor
from utils.sheets_manager import SheetsManager

class ZaloListener:
    def __init__(self, ai_processor: AIProcessor, sheets_manager: SheetsManager):
        self.ai = ai_processor
        self.sheets = sheets_manager

    def start_listening(self, headless=False):
        print("[ZALO LISTENER] Đang khởi chạy trình duyệt đọc tin nhắn Zalo...")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_PROFILE_DIR),
                headless=headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = context.new_page()
            page.goto("https://chat.zalo.me")
            
            print("[ZALO LISTENER] Đang kiểm tra trạng thái đăng nhập...")
            page.wait_for_timeout(5000)

            print("[ZALO LISTENER] Bắt đầu vòng lặp lắng nghe tin nhắn mới (Ấn Ctrl+C để dừng)...")
            processed_messages = set()

            try:
                while True:
                    # Lấy các đoạn tin nhắn thoại/văn bản mới xuất hiện trên UI
                    # LƯU Ý: Selector bên dưới tùy thuộc vào giao diện Zalo Web hiện tại
                    messages = page.query_selector_all(".msg-item")
                    for msg in messages:
                        text = msg.inner_text().strip()
                        if text and text not in processed_messages:
                            processed_messages.add(text)
                            print(f"\n[ZALO NEW MSG] Phát hiện tin nhắn: {text[:50]}...")
                            
                            # Xử lý qua AI
                            ai_res = self.ai.process_zalo_message(text)
                            if ai_res.get("is_real_estate", False):
                                print("[ZALO LISTENER] Phát hiện tin BĐS phù hợp!")
                                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                self.sheets.append_lead(now_str, "Zalo Group/User", text, ai_res)

                    time.sleep(5)
            except KeyboardInterrupt:
                print("\n[ZALO LISTENER] Đã dừng lắng nghe Zalo.")
            finally:
                context.close()