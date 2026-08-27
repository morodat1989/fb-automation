import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class SheetsManager:

  def __init__(
      self,
      json_key_path: str = "key/credentials.json",
      sheet_name: str = "BDS_Auto_Post",
  ):
    self.json_key_path = json_key_path
    self.sheet_name = sheet_name
    self.sheet = None

  def connect(self) -> bool:
    if not os.path.exists(self.json_key_path):
      print(
          f"Lỗi: Không tìm thấy file khóa bảo mật tại '{self.json_key_path}'"
      )
      return False

    try:
      scope = [
          "https://spreadsheets.google.com/feeds",
          "https://www.googleapis.com/auth/drive",
      ]
      creds = ServiceAccountCredentials.from_json_keyfile_name(
          self.json_key_path, scope
      )
      client = gspread.authorize(creds)
      self.sheet = client.open(self.sheet_name).sheet1
      return True
    except Exception as e:
      print(f"Lỗi kết nối Google Sheet: {e}")
      return False

  def append_bds_data(
      self,
      bds_data: dict,
      image_paths: list = [],
      status: str = "CHỜ_ĐĂNG",
      loai_bds: str = "CHƯA_PHÂN_LOẠI",
  ) -> bool:
    if not self.sheet and not self.connect():
      return False

    try:
      current_time = datetime.datetime.now().strftime("%H:%M %d/%m/%Y")

      row = [
          bds_data.get("tieu_de", ""),  # Cột A: Tiêu đề
          bds_data.get("gia", ""),  # Cột B: Giá
          bds_data.get("dien_tich", ""),  # Cột C: Diện tích
          bds_data.get("dia_chi", ""),  # Cột D: Địa chỉ
          bds_data.get("mo_ta_marketplace", ""),  # Cột E: Mô tả Marketplace
          bds_data.get("mo_ta_hoinhom", ""),  # Cột F: Mô tả Hội nhóm
          ", ".join(bds_data.get("tu_khoa", [])),  # Cột G: Từ khóa SEO
          status,  # Cột H: Trạng thái
          ";".join(image_paths),  # Cột I: Đường dẫn ảnh
          current_time,  # Cột J: Thời gian đăng
          loai_bds,  # Cột K: Loại BĐS
      ]
      self.sheet.append_row(row)
      print(
          f"-> ĐÃ LƯU VÀO SHEET: [{loai_bds}] |"
          f" {bds_data.get('tieu_de', '')}"
      )
      return True
    except Exception as e:
      print(f"Lỗi khi ghi dữ liệu vào Sheet: {e}")
      return False

  def get_pending_posts(self, loai_bds_filter: str = None) -> list:
    """Lấy các bài 'CHỜ_ĐĂNG', lọc theo Loại BĐS nếu có chỉ định."""
    if not self.sheet and not self.connect():
      return []

    try:
      all_rows = self.sheet.get_all_values()
      pending_list = []

      # Bỏ qua hàng tiêu đề A1:K1 (index 0)
      for idx, row in enumerate(all_rows[1:], start=2):
        if len(row) < 8:
          continue

        status = row[7].strip()
        loai = row[10].strip() if len(row) >= 11 else ""

        if status == "CHỜ_ĐĂNG":
          if loai_bds_filter is None or loai == loai_bds_filter:
            pending_list.append({
                "row_index": idx,
                "tieu_de": row[0],
                "gia": row[1],
                "dien_tich": row[2],
                "dia_chi": row[3],
                "mo_ta_marketplace": row[4],
                "mo_ta_hoinhom": row[5],
                "tu_khoa": row[6],
                "status": row[7],
                "image_paths": row[8].split(";") if row[8] else [],
                "time": row[9] if len(row) >= 10 else "",
                "loai_bds": loai,
            })
      return pending_list
    except Exception as e:
      print(f"Lỗi đọc dữ liệu từ Sheet: {e}")
      return []

  def update_post_status(
      self, row_index: int, status: str = "ĐÃ_ĐĂNG"
  ) -> bool:
    """Cập nhật Trạng thái tại Cột H (Cột 8)."""
    if not self.sheet and not self.connect():
      return False

    try:
      self.sheet.update_cell(row_index, 8, status)
      return True
    except Exception as e:
      print(f"Lỗi cập nhật trạng thái hàng {row_index}: {e}")
      return False