import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class SheetsManager:

  def __init__(
      self,
      json_key_path: str = "credentials.json",
      sheet_name: str = "BDS_Auto_Post",
  ):
    self.json_key_path = json_key_path
    self.sheet_name = sheet_name
    self.sheet = None

  def connect(self) -> bool:
    """Kết nối tới Google Sheets API."""
    if not os.path.exists(self.json_key_path):
      print(
          f"Lỗi: Không tìm thấy file '{self.json_key_path}'. Hãy đảm bảo bạn đã"
          " đặt file credentials.json vào thư mục D:\\Tool\\fb"
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
      print(f"-> Kết nối thành công tới Google Sheet: '{self.sheet_name}'")
      return True
    except Exception as e:
      print(f"Lỗi kết nối Google Sheet: {e}")
      return False

  def append_bds_data(self, bds_data: dict, status: str = "PENDING") -> bool:
    """Ghi một dòng dữ liệu bài đăng BĐS vào dòng cuối cùng của Trang tính."""
    if not self.sheet:
      if not self.connect():
        return False

    try:
      row = [
          bds_data.get("title", ""),
          bds_data.get("price", ""),
          bds_data.get("area", ""),
          bds_data.get("address", ""),
          bds_data.get("marketplace_description", ""),
          bds_data.get("group_description", ""),
          ", ".join(bds_data.get("keywords", [])),
          status,  # Trạng thái để tool tự động đăng nhận biết (PENDING / SUCCESS)
      ]
      self.sheet.append_row(row)
      print("-> ĐÃ LƯU THÀNH CÔNG VÀO GOOGLE SHEET!")
      return True
    except Exception as e:
      print(f"Lỗi khi ghi dòng vào Google Sheet: {e}")
      return False