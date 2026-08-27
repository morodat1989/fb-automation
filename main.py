import sys
import os

from login_setup import run_login_setup
from core.ai_processor import AIProcessor
from utils.sheets_manager import SheetsManager
from core.zalo_listener import ZaloListener
from core.fb_poster import FBPoster

def main():
    print("==================================================")
    print("      HỆ THỐNG TỰ ĐỘNG HÓA ZALO -> FB POSTER      ")
    print("==================================================")
    print("1. [Setup] Đăng nhập & Tạo Session (Zalo/Facebook)")
    print("2. [Run] Lắng nghe Zalo -> AI Xử lý -> Lưu Sheet")
    print("3. [Run] Đọc Sheet -> Đăng bài tự động lên Facebook")
    print("4. [Auto] Luồng tự động trọn gói (Listener + Auto Post)")
    print("5. Thoát")
    print("==================================================")
    
    choice = input("Nhập lựa chọn của bạn (1-5): ").strip()

    if choice == '1':
        run_login_setup()

    elif choice == '2':
        ai = AIProcessor()
        sheets = SheetsManager()
        listener = ZaloListener(ai_processor=ai, sheets_manager=sheets)
        listener.start_listening(headless=False)

    elif choice == '3':
        sheets = SheetsManager()
        poster = FBPoster(sheets_manager=sheets)
        group_url = input("Nhập URL nhóm/Trang FB muốn đăng (để trống nếu đăng Wall cá nhân): ").strip()
        poster.post_pending_items(group_url=group_url if group_url else None, headless=False)

    elif choice == '4':
        print("\n[AUTO PIPELINE] Đang kích hoạt luồng tự động...")
        ai = AIProcessor()
        sheets = SheetsManager()
        listener = ZaloListener(ai_processor=ai, sheets_manager=sheets)
        poster = FBPoster(sheets_manager=sheets)

        # Chạy listener trước
        listener.start_listening(headless=False)
        # Sau khi dừng Listener (Ctrl+C), chạy poster
        poster.post_pending_items(headless=False)

    elif choice == '5':
        print("Đã thoát chương trình.")
        sys.exit(0)
    else:
        print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()