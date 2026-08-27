import json
import logging
from typing import Dict, Any
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

logger = logging.getLogger("AIProcessor")

class AIProcessor:
    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY chưa được cấu hình trong file .env")
            raise ValueError("GEMINI_API_KEY chưa được thiết lập!")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def process_zalo_message(self, raw_message: str) -> Dict[str, Any]:
        """
        Phân tích tin nhắn Zalo bất động sản và chuyển đổi thành dạng bài đăng Facebook.
        """
        if not raw_message or not raw_message.strip():
            return self._default_fallback(raw_message)

        prompt = f"""
        Bạn là một chuyên gia marketing bất động sản. Hãy phân tích tin nhắn thô sau từ Zalo:
        "{raw_message}"

        Hãy trích xuất thông tin và viết lại thành một bài đăng Facebook thu hút người mua.
        Trả về kết quả dưới dạng JSON duy nhất với cấu trúc:
        {{
            "is_real_estate": true/false,
            "title": "Tiêu đề ngắn thu hút",
            "price": "Giá bán",
            "location": "Vị trí",
            "fb_content": "Nội dung bài đăng Facebook hoàn chỉnh kèm hashtag và icon"
        }}
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
              
            if not response or not response.text:
                logger.warning("Gemini API trả về response trống hoặc bị chặn bởi Safety Filter.")
                return self._default_fallback(raw_message)

            data = json.loads(response.text.strip())
            
            # Validate cấu trúc JSON đầu ra
            required_keys = ["is_real_estate", "title", "price", "location", "fb_content"]
            for key in required_keys:
                if key not in data:
                    data[key] = "" if key != "is_real_estate" else False

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Lỗi parse JSON từ kết quả AI: {e}")
            return self._default_fallback(raw_message)
        except Exception as e:
            logger.error(f"Lỗi không xác định khi gọi Gemini API: {e}", exc_info=True)
            return self._default_fallback(raw_message)

    def _default_fallback(self, raw_message: str) -> Dict[str, Any]:
        return {
            "is_real_estate": False,
            "title": "",
            "price": "",
            "location": "",
            "fb_content": raw_message
        }