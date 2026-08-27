import os
import json
import google.generativeai as genai
from config import GEMINI_API_KEY

class AIProcessor:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY chưa được thiết lập trong .env")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

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
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            
            # Làm sạch mã JSON trả về từ Markdown
            if text_response.startswith("```json"):
                text_response = text_response[7:-3].strip()
            elif text_response.startswith("```"):
                text_response = text_response[3:-3].strip()

            data = json.loads(text_response)
            return data
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
    # Test nhanh
    ai = AIProcessor()
    test_res = ai.process_zalo_message("Bán nhà Cầu Giấy 50m2 x 5 tầng, giá 6.5 tỷ, ô tô đỗ cửa. LH 0987654321")
    print(json.dumps(test_res, ensure_ascii=False, indent=2))