import asyncio
from core.browser_manager import connect_cdp, close_cdp
from modules.feed_actions import run_feed_seeding
from modules.reels_actions import run_reels_seeding  # 1. THÊM IMPORT Ở ĐẦU FILE
from utils.logger import log_info, log_error

async def main():
    # Kết nối tới Chrome đang mở qua CDP Port 9222
    browser, context, page = await connect_cdp()
    if not page:
        log_error("Không thể kết nối Chrome CDP!")
        return

    while True:
        print("\n==========================================")
        print("   SYSTEM FACEBOOK AUTOMATION MENU        ")
        print("==========================================")
        print("1. Seeding Newsfeed (Lướt, Like, Comment)")
        print("2. Seeding Reels (Lướt Reels, Thả tim, Comment)") # In menu lựa chọn
        print("0. Thoát chương trình")
        print("==========================================")
        
        choice = input("👉 Nhập lựa chọn của bạn (0-2): ").strip()

        if choice == "1":
            await run_feed_seeding(page)
            
        elif choice == "2":
            # 2. THÊM KHỐI LỰA CHỌN NÀY NGAY SAU CHOICE == "1"
            await run_reels_seeding(page, total_reels=8)
            
        elif choice == "0":
            log_info("Đang thoát chương trình...")
            break
        else:
            print("❌ Lựa chọn không hợp lệ. Vui lòng thử lại!")

    await close_cdp(browser)

if __name__ == "__main__":
    asyncio.run(main())