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
        self.processed_messages = set()

    def check_new_messages(self, page) -> int:
        """Hàm quét tin nhắn trên Zalo Web hiện tại (dùng chung cho cả chạy lẻ và Auto)"""
        new_count = 0
        try:
            messages = page.query_selector_all(".msg-item, .chat-message, [data-id]")
            for msg in messages:
                text = msg.inner_text().strip()
                if text and text not in self.processed_messages and len(text) > 10:
                    self.processed_messages.add(text)
                    print(f"\n[ZALO NEW MSG] Phát hiện tin nhắn: {text[:60]}...")

                    ai_res = self.ai.process_zalo_message(text)
                    if ai_res.get("is_real_estate", False):
                        print("[ZALO LISTENER] => Đã xác nhận bài BĐS! Ghi vào Sheet...")
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.sheets.append_lead(now_str, "Zalo Group/User", text, ai_res)
                        new_count += 1
                    else:
                        print("[ZALO LISTENER] => Không phải bài BĐS, bỏ qua.")
        except Exception as e:
            print(f"[ZALO ERROR] Lỗi khi đọc tin nhắn Zalo: {e}")
        return new_count

    def start_listening(self, headless=False):
        print("[ZALO LISTENER] Đang khởi chạy trình duyệt Zalo...")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_PROFILE_DIR),
                headless=headless,
                viewport={'width': 1366, 'height': 768},
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            page = context.new_page()
            page.goto("https://chat.zalo.me", wait_until="domcontentloaded")

            print("[ZALO LISTENER] Bắt đầu lắng nghe tin nhắn... (Nhấn Ctrl+C để dừng)")
            try:
                while True:
                    self.check_new_messages(page)
                    time.sleep(5)
            except KeyboardInterrupt:
                print("\n[ZALO LISTENER] Đã dừng lắng nghe Zalo.")
            finally:
                context.close()