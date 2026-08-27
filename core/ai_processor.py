import os
import json
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

class AIProcessor:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY chưa được thiết lập trong file .env")
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def process_zalo_message(self, raw_message: str) -> dict:
        """
        Phân tích tin nhắn Zalo bất động sản và tạo nội dung đăng Facebook
        """
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
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # An toàn chống crash nếu Gemini chặn safety filter
            if not response or not response.text:
                print("[AI WARNING] AI không trả về văn bản (có thể bị chặn bởi bộ lọc nội dung).")
                return {
                    "is_real_estate": False,
                    "title": "",
                    "price": "",
                    "location": "",
                    "fb_content": raw_message
                }

            text_response = response.text.strip()
            return json.loads(text_response)

        except Exception as e:
            print(f"[AI ERROR] Lỗi khi xử lý với Gemini: {e}")
            return {
                "is_real_estate": False,
                "title": "",
                "price": "",
                "location": "",
                "fb_content": raw_message
            }

if __name__ == "__main__":
    ai = AIProcessor()
    test_res = ai.process_zalo_message("Bán nhà Cầu Giấy 50m2 x 5 tầng, giá 6.5 tỷ, LH 0987654321")
    print(json.dumps(test_res, ensure_ascii=False, indent=2))