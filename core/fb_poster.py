import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.sheets_manager import SheetsManager

PROFILE_DIR = os.path.abspath("fb_session")


def run_auto_poster(target_loai_bds: str = None):
  sheets_tool = SheetsManager(
      json_key_path="key/credentials.json", sheet_name="BDS_Auto_Post"
  )

  if target_loai_bds:
    print(f"-> Đang lọc danh sách bài CHỜ_ĐĂNG thuộc loại: [{target_loai_bds}]")
  else:
    print("-> Đang lấy TOÀN BỘ bài CHỜ_ĐĂNG...")

  posts = sheets_tool.get_pending_posts(loai_bds_filter=target_loai_bds)

  if not posts:
    print("-> Không tìm thấy bài nào thỏa mãn điều kiện để đăng.")
    return

  print(f"-> Tìm thấy {len(posts)} bài chờ đăng.")

  with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False,
        args=["--start-maximized"],
    )
    page = browser.pages[0] if browser.pages else browser.new_page()

    for item in posts:
      print("\n==========================================")
      print(
          f"ĐANG ĐĂNG BÀI [{item['loai_bds']}]: {item['tieu_de']} (Hàng"
          f" {item['row_index']})"
      )

      try:
        # Giả lập thời gian thực thi đăng bài
        time.sleep(3)

        # Cập nhật trạng thái bài viết sau khi đăng xong thành công
        sheets_tool.update_post_status(item["row_index"], status="ĐÃ_ĐĂNG")
        print(f"-> Đã cập nhật trạng thái ĐÃ_ĐĂNG cho hàng {item['row_index']}")

      except Exception as e:
        print(f"Lỗi khi đăng bài hàng {item['row_index']}: {e}")

    browser.close()


if __name__ == "__main__":
  if len(sys.argv) > 1:
    selected_loai = sys.argv[1]
  else:
    print("--- CHỌN LOẠI BĐS CẦN ĐĂNG HÔM NAY ---")
    print("1. CHO_THUÊ")
    print("2. BÁN_CAO_CẤP")
    print("3. BÁN_ĐẦU_THẤP")
    print("4. MẶT_PHỐ_ĐẤT_NỀN")
    print("5. BUNG_LỤA")
    print("6. ĐĂNG TẤT CẢ")

    choice = input("Nhập lựa chọn (1-6 hoặc gõ tên trực tiếp): ").strip()
    mapping = {
        "1": "CHO_THUÊ",
        "2": "BÁN_CAO_CẤP",
        "3": "BÁN_ĐẦU_THẤP",
        "4": "MẶT_PHỐ_ĐẤT_NỀN",
        "5": "BUNG_LỤA",
        "6": None,
    }
    selected_loai = mapping.get(choice, choice if choice else None)

  run_auto_poster(target_loai_bds=selected_loai)