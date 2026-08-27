import json
import sys
from utils.logger import get_logger
from core.browser_manager import BrowserManager
from modules.feed_actions import FeedActions

logger = get_logger("Main")


def load_config() -> dict:
    """Đọc cấu hình hệ thống từ config.json."""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Lỗi đọc file config.json: {e}")
        sys.exit(1)


def run_feed_scenario(cdp_port: int) -> None:
    """Khởi chạy kịch bản lướt Newsfeed & Seeding."""
    manager = BrowserManager(cdp_port=cdp_port)
    page = manager.connect()

    if not page:
        return

    try:
        # Khởi tạo mô-đun tương tác Feed
        feed_module = FeedActions(page)

        # Chạy kịch bản: Cuộn 6 lần, 40% xác suất Like, 20% xác suất Comment
        feed_module.browse_and_interact(
            scroll_count=6,
            like_prob=0.40,
            comment_prob=0.20,
            comments_list=[
                "Bài viết hữu ích quá!",
                "Cảm ơn bạn đã chia sẻ nhé",
                "Up bài cho mọi người cùng thấy",
                "Quan tâm ạ",
                "Great post!"
            ]
        )
    except Exception as e:
        logger.error(f"Lỗi trong quá trình chạy kịch bản Feed: {e}")
    finally:
        manager.close()


def show_main_menu() -> None:
    print("\n" + "=" * 50)
    print("   HỆ THỐNG TỰ ĐỘNG HÓA FACEBOOK (PLAYWRIGHT)")
    print("=" * 50)
    print("1. Mở Chrome / Quản lý Profile (login_setup.py)")
    print("2. Chạy kịch bản Lướt Feed & Seeding (Feed Actions)")
    print("3. Kiểm tra kết nối Chrome CDP")
    print("0. Thoát")
    print("=" * 50)


def main() -> None:
    config = load_config()
    cdp_port = config.get("cdp_port", 9222)
    logger.info("Đã khởi tạo hệ thống thành công.")

    while True:
        show_main_menu()
        choice = input("Nhập lựa chọn của bạn (0-3): ").strip()

        if choice == "1":
            try:
                import login_setup
                login_setup.main()
            except Exception as e:
                logger.error(f"Lỗi khởi chạy login_setup: {e}")

        elif choice == "2":
            logger.info("Bắt đầu thực thi kịch bản Feed Actions...")
            run_feed_scenario(cdp_port)

        elif choice == "3":
            manager = BrowserManager(cdp_port=cdp_port)
            page = manager.connect()
            if page:
                print(f"\n[OK] Kết nối CDP thành công! Tiêu đề tab hiện tại: '{page.title()}'")
                manager.close()
            else:
                print("\n[FAIL] Không thể kết nối. Hãy bấm phím 1 để bật Chrome trước.")

        elif choice == "0":
            logger.info("Đã thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn lại.")


if __name__ == "__main__":
    main()