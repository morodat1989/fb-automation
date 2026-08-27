import json
import os
import sys

# Đảm bảo import được các module trong utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from google.genai import errors, types
from utils.sheets_manager import SheetsManager

# 1. Cấu hình Gemini API Key
os.environ["GEMINI_API_KEY"] = "AIzaSyAF8uH-1Bq34CrmsPbLODLJnAXdcBpC-qc"

# 2. Khởi tạo Client Gemini
client = genai.Client()

# 3. Dữ liệu Zalo BĐS thô làm mẫu
zalo_raw = """
Chủ gửi bán gấp căn 2PN Vinhomes Smart City full đồ đẹp. 
DT 55m2, tầng trung view thoáng. Sổ đỏ chính chủ sẵn sàng giao dịch.
Giá chốt 3.2 tỷ bao phí. Lh 0912345678 xem nhà 24/7.
"""

# 4. Prompt yêu cầu trích xuất dữ liệu định dạng JSON
prompt = f"""
Bạn là Chuyên gia Copywriter Bất động sản và Tối ưu hóa SEO Facebook Marketplace.

Nhiệm vụ: Phân tích tin nhắn Zalo thô bên dưới và chuyển đổi thành cấu trúc JSON hợp lệ để lưu trữ vào Google Sheet.

Yêu cầu dữ liệu trong JSON:
- title: Tiêu đề chuẩn SEO (dưới 65 ký tự, chứa từ khóa chính, địa điểm, giá bán).
- price: Giá niêm yết ngắn gọn (ví dụ: "3.2 tỷ").
- area: Diện tích (ví dụ: "55m²").
- address: Địa chỉ/Tên dự án ngắn gọn (ví dụ: "Vinhomes Smart City, Nam Từ Liêm").
- marketplace_description: Nội dung mô tả cho FB Marketplace (Tập trung thông số, tối giản, loại bỏ hoàn toàn các từ ngữ vi phạm chính sách FB).
- group_description: Nội dung mô tả chi tiết cho FB Group/Profile (Nổi bật tiện ích, lý do nên mua, lời kêu gọi liên hệ).
- keywords: Mảng chứa 3-5 từ khóa SEO phục vụ tìm kiếm.

Nội dung Zalo thô:
{zalo_raw}
"""

# 5. Danh sách model ưu tiên xử lý
MODELS_TO_TRY = ["gemini-3.6-flash", "gemini-1.5-flash"]

response = None
for model_name in MODELS_TO_TRY:
  try:
    print(f"Đang xử lý dữ liệu với model: {model_name}...")
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )
    print(f"-> Thành công với model: {model_name}\n")
    break
  except errors.APIError as e:
    if e.code == 404:
      print(f"Model {model_name} bị 404, đang đổi sang model tiếp theo...")
      continue
    else:
      print(f"Lỗi API: {e}")
      break
  except Exception as e:
    print(f"Lỗi không xác định: {e}")
    break

# 6. Parse JSON và tự động đẩy vào Google Sheet
if response and response.text:
  try:
    bds_data = json.loads(response.text)
    print("=== NỘI DUNG DỮ LIỆU ĐÃ TẠO ===")
    print(json.dumps(bds_data, ensure_ascii=False, indent=2))
    print("===============================\n")

    # Gọi SheetsManager để ghi dữ liệu vào Google Sheet
    sheets_tool = SheetsManager(
        json_key_path="key/credentials.json", sheet_name="BDS_Auto_Post"
    )
    sheets_tool.append_bds_data(bds_data, status="PENDING")

  except json.JSONDecodeError as e:
    print(f"Lỗi parse JSON: {e}")
    print("Nội dung gốc nhận từ API:")
    print(response.text)
else:
  print("Không thể lấy dữ liệu từ Gemini. Kiểm tra lại API Key hoặc kết nối.")