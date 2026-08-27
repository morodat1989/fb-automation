import datetime
import hashlib
import os
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ai_processor import process_zalo_message

TARGET_GROUPS_MAP = {
    "VSA BẢNG HÀNG CAO CẤP": "BÁN_CAO_CẤP",
    "VSA - Bảng Hàng Thuê": "CHO_THUÊ",
    "Bung Lụa - VSA": "BUNG_LỤA",
    "Nhà Mặt Phố, Đất Nền Kh...": "MẶT_PHỐ_ĐẤT_NỀN",
    "VSA - Bảng Hàng Đầu Thấp": "BÁN_ĐẦU_THẤP",
}

NUM_SCROLL_HISTORY = 5
PROFILE_DIR = os.path.abspath("zalo_session")
IMAGE_DIR = os.path.abspath("images")
os.makedirs(IMAGE_DIR, exist_ok=True)


def download_image(url: str, save_prefix: str) -> str:
  try:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_path = os.path.join(IMAGE_DIR, f"{save_prefix}_{timestamp}.jpg")
    urllib.request.urlretrieve(url, file_path)
    return file_path
  except Exception as e:
    print(f"Lỗi tải ảnh ({url}): {e}")
    return ""


def get_msg_hash(text: str) -> str:
  return hashlib.md5(text.strip().encode("utf-8")).hexdigest()


def process_chat_messages(page, processed_hashes: set, loai_bds: str):
  messages = page.query_selector_all(
      '.msg-item, [class*="msg-item"], .message-view'
  )

  for msg in messages:
    msg_text = msg.inner_text().strip()
    if not msg_text:
      continue

    msg_hash = get_msg_hash(msg_text)
    if msg_hash in processed_hashes:
      continue

    keywords_check = [
        "bán",
        "chính chủ",
        "giá",
        "tỷ",
        "triệu",
        "m2",
        "phòng ngủ",
        "sổ đỏ",
        "dt",
        "lô",
        "đất",
        "cho thuê",
        "phố",
    ]
    if not any(kw in msg_text.lower() for kw in keywords_check):
      processed_hashes.add(msg_hash)
      continue

    print(f"\n[{loai_bds}] -> PHÁT HIỆN TIN BĐS:\n{msg_text[:100]}...")

    image_elements = msg.query_selector_all("img")
    downloaded_images = []

    for idx, img in enumerate(image_elements):
      src = img.get_attribute("src")
      if src and "blob:" not in src and "http" in src:
        img_path = download_image(src, f"zalo_img_{idx}")
        if img_path:
          downloaded_images.append(img_path)

    process_zalo_message(
        zalo_raw=msg_text, image_paths=downloaded_images, loai_bds=loai_bds
    )
    processed_hashes.add(msg_hash)


def start_zalo_listener():
  with sync_playwright() as p:
    print("-> Đang mở Zalo Web...")
    browser = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False,
        args=["--start-maximized"],
    )

    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto("https://chat.zalo.me")

    try:
      page.wait_for_selector('input[placeholder*="Tìm kiếm"]', timeout=120000)
      print("-> Đã đăng nhập Zalo thành công!")
    except Exception:
      print("-> Hết thời gian chờ đăng nhập.")
      browser.close()
      return

    processed_hashes = set()

    while True:
      try:
        for group_name, loai_bds in TARGET_GROUPS_MAP.items():
          print(f"\n------------------------------------------")
          print(f"ĐANG TRUY CẬP NHÓM: [{group_name}] ({loai_bds})")

          search_input = page.wait_for_selector(
              'input[placeholder*="Tìm kiếm"]'
          )
          search_input.click()
          search_input.fill(group_name)
          time.sleep(1.5)

          group_item = page.query_selector(f'text="{group_name}"')
          if group_item:
            group_item.click()
            time.sleep(2)

            for _ in range(NUM_SCROLL_HISTORY):
              page.mouse.wheel(0, -3000)
              time.sleep(1)

            process_chat_messages(page, processed_hashes, loai_bds)
          else:
            print(f"   -> Không tìm thấy nhóm '{group_name}'")

        print("\n-> Đã quét xong tất cả nhóm chỉ định. Nghỉ 60 giây...")
        time.sleep(60)

      except KeyboardInterrupt:
        print("\n-> Đã dừng Tool Lắng nghe Zalo.")
        break
      except Exception as e:
        print(f"Lỗi hệ thống: {e}")
        time.sleep(5)

    browser.close()


if __name__ == "__main__":
  start_zalo_listener()