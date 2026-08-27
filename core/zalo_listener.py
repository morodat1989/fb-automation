import json
import hashlib
import logging
from datetime import datetime
from typing import Set
from playwright.sync_api import Page, sync_playwright
from config import BROWSER_PROFILE_DIR, STATE_FILE_PATH
from core.ai_processor import AIProcessor
from utils.sheets_manager import SheetsManager

logger = logging.getLogger("ZaloListener")

class ZaloListener:
    def __init__(self, ai_processor: AIProcessor, sheets_manager: SheetsManager) -> None:
        self.ai = ai_processor
        self.sheets = sheets_manager
        self.processed_hashes: Set[str] = self._load_state()

    def _load_state(self) -> Set[str]:
        if STATE_FILE_PATH.exists():
            try:
                with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except Exception as e:
                logger.error(f"Lỗi khi đọc file state: {e}")
        return set()

    def _save_state(self) -> None:
        try:
            with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(list(self.processed_hashes), f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Lỗi khi lưu file state: {e}")

    def _hash_text(self, text: str) -> str:
        return hashlib.md5(text.strip().encode("utf-8")).hexdigest()

    def check_new_messages(self, page: Page) -> int:
        new_count = 0
        try:
            messages = page.query_selector_all(".msg-item, .chat-message, [data-id]")
            for msg in messages:
                text = msg.inner_text().strip()
                if not text or len(text) <= 10:
                    continue

                msg_hash = self._hash_text(text)
                if msg_hash in self.processed_hashes:
                    continue

                # Đánh dấu đã đọc trước khi xử lý để chống trùng
                self.processed_hashes.add(msg_hash)
                self._save_state()

                logger.info(f"[ZALO] Tin nhắn mới: {text[:60]}...")
                ai_res = self.ai.process_zalo_message(text)

                if ai_res.get("is_real_estate", False):
                    logger.info("[ZALO] => Nội dung BĐS hợp lệ. Đang lưu Google Sheet...")
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.sheets.append_lead(now_str, "Zalo Listener", text, ai_res)
                    new_count += 1
                else:
                    logger.info("[ZALO] => Không phải bài BĐS, bỏ qua.")

        except Exception as e:
            logger.error(f"Lỗi khi quét DOM Zalo: {e}", exc_info=True)
        return new_count

    def start_listening(self, headless: bool = False) -> None:
        logger.info("Khởi động Zalo Listener standalone...")
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_PROFILE_DIR),
                headless=headless,
                viewport={'width': 1366, 'height': 768},
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            page = context.new_page()
            page.goto("https://chat.zalo.me", wait_until="domcontentloaded")

            logger.info("Zalo Listener đang hoạt động... (Ctrl+C để dừng)")
            try:
                while True:
                    self.check_new_messages(page)
                    page.wait_for_timeout(5000)
            except KeyboardInterrupt:
                logger.info("Đã dừng Zalo Listener.")
            finally:
                context.close()