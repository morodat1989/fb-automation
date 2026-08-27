import time
import logging
from playwright.sync_api import sync_playwright
from config import BROWSER_PROFILE_DIR, ZALO_URL

logger = logging.getLogger("ZaloListener")

class ZaloListener:
    def __init__(self, ai_processor, sheet_manager):
        self.ai_processor = ai_processor
        self.sheet_manager = sheet_manager

    def _is_valid_group(self, group_name: str) -> bool:
        """Chỉ chấp nhận đúng 4 nhóm bảng hàng mục tiêu của bạn"""
        if not group_name:
            return False
        
        group_lower = group_name.lower()
        
        # Danh sách từ khóa nhận diện chuẩn xác 4 nhóm yêu cầu
        target_keywords = [
            "vsa bảng hàng cao cấp",
            "vsa - bảng hàng thuê",
            "nhà mặt phố",
            "vsa - bảng hàng đầu thấp"
        ]
        
        # Chỉ trả về True nếu tên nhóm chứa một trong các từ khóa trên
        return any(kw in group_lower for kw in target_keywords)

    def start_listening(self):
        logger.info("Khởi động Zalo Listener bằng Google Chrome...")
        
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
                        "--disable-web-security"
                    ]
                )

                page = context.new_page()
                page.goto(ZALO_URL, wait_until="domcontentloaded")
                logger.info("Zalo Listener đang hoạt động... (Ctrl+C để dừng)")

                processed_messages = set()

                while True:
                    try:
                        page.wait_for_selector(".chat-item, .pane-message-list", timeout=5000)
                        chat_items = page.locator(".chat-item").all()
                        
                        for chat in chat_items:
                            try:
                                title_elem = chat.locator(".chat-name, .name").first
                                message_elem = chat.locator(".chat-message, .message-content, .preview-message").first
                                
                                if not title_elem.is_visible() or not message_elem.is_visible():
                                    continue

                                group_name = title_elem.inner_text().strip()
                                message_text = message_elem.inner_text().strip()
                                
                                msg_id = f"{group_name}:{message_text}"

                                # 1. Lọc nhóm: Chỉ cho phép 4 nhóm mục tiêu đi tiếp
                                if not self._is_valid_group(group_name):
                                    continue

                                # 2. Chống lặp tin nhắn cũ
                                if msg_id in processed_messages:
                                    continue

                                logger.info(f"[ZALO] Phát hiện tin nhắn mới từ nhóm mục tiêu [{group_name}]:\n{message_text}")
                                
                                processed_messages.add(msg_id)
                                if len(processed_messages) > 500:
                                    processed_messages.pop()

                                # 3. Gửi AI xử lý
                                ai_result = self.ai_processor.process_zalo_message(message_text)
                                
                                if ai_result and ai_result.get("is_property"):
                                    logger.info(f"[ZALO] => Bài viết hợp lệ, đang lưu vào Google Sheet...")
                                    self.sheet_manager.save_to_sheet(ai_result)
                                else:
                                    logger.info(f"[ZALO] => Không phải bài BĐS, bỏ qua.")

                            except Exception:
                                continue

                        time.sleep(3)

                    except Exception as loop_e:
                        logger.warning(f"Đang chờ Zalo đồng bộ / kết nối lại... ({loop_e})")
                        time.sleep(5)

            except Exception as e:
                logger.error(f"Lỗi khởi chạy Zalo Listener: {e}")