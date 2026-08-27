import json
import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from google.genai import types
from utils.sheets_manager import SheetsManager

NEW_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GEMINI_API_KEY"] = os.getenv(
    "GEMINI_API_KEY", NEW_GEMINI_API_KEY
)

client = genai.Client()


def process_zalo_message(
    zalo_raw: str,
    image_paths: list = [],
    loai_bds: str = "CHƯA_PHÂN_LOẠI",
):
  contents = []
  valid_image_paths = []

  for img_path in image_paths:
    if os.path.exists(img_path):
      try:
        contents.append(Image.open(img_path))
        valid_image_paths.append(os.path.abspath(img_path))
      except Exception as e:
        print(f"Không đọc được ảnh {img_path}: {e}")

  prompt = f"""
Bạn là Chuyên gia Copywriter Bất động sản và Tối ưu hóa SEO Facebook Marketplace.

Nhiệm vụ: Phân tích tin nhắn Zalo thô thuộc phân loại [{loai_bds}] và các hình ảnh đính kèm để trích xuất dữ liệu chuẩn hóa dạng JSON.

Yêu cầu các khóa JSON bằng tiếng Việt:
- tieu_de: Tiêu đề chuẩn SEO (dưới 65 ký tự, chứa từ khóa chính, địa điểm, giá).
- gia: Giá niêm yết ngắn gọn (ví dụ: "3.2 tỷ" hoặc "15 triệu/tháng").
- dien_tich: Diện tích (ví dụ: "55m²").
- dia_chi: Địa chỉ/Dự án ngắn gọn.
- mo_ta_marketplace: Nội dung mô tả tối giản cho FB Marketplace.
- mo_ta_hoinhom: Nội dung mô tả chi tiết thu hút cho FB Group.
- tu_khoa: Mảng chứa 3-5 từ khóa SEO tìm kiếm.

Nội dung Zalo:
{zalo_raw}
"""
  contents.append(prompt)

  MODELS_TO_TRY = ["gemini-3.6-flash", "gemini-1.5-flash"]
  response = None

  for model_name in MODELS_TO_TRY:
    try:
      response = client.models.generate_content(
          model=model_name,
          contents=contents,
          config=types.GenerateContentConfig(
              response_mime_type="application/json"
          ),
      )
      break
    except Exception as e:
      print(f"Lỗi AI ({model_name}): {e}")

  if response and response.text:
    try:
      bds_data = json.loads(response.text)
      sheets_tool = SheetsManager(
          json_key_path="key/credentials.json", sheet_name="BDS_Auto_Post"
      )
      sheets_tool.append_bds_data(
          bds_data=bds_data,
          image_paths=valid_image_paths,
          status="CHỜ_ĐĂNG",
          loai_bds=loai_bds,
      )
    except json.JSONDecodeError as e:
      print(f"Lỗi parse JSON từ Gemini: {e}")