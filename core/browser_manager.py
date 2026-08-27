from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from utils.logger import log_info, log_error, log_warning

_playwright_instance = None

async def connect_cdp(cdp_url: str = "http://localhost:9222"):
    """
    Kết nối tới Google Chrome đang mở sẵn qua cổng CDP 9222.
    Trả về tuple: (browser, context, page)
    """
    global _playwright_instance
    try:
        _playwright_instance = await async_playwright().start()
        log_info(f"🔌 Đang kết nối tới Chrome qua CDP: {cdp_url}...")
        
        browser = await _playwright_instance.chromium.connect_over_cdp(cdp_url)
        
        if not browser.contexts:
            log_error("X Không tìm thấy Context/Profile nào trong Chrome!")
            return None, None, None
            
        context = browser.contexts[0]
        pages = context.pages
        
        # Lấy tab đang mở hoặc tạo tab mới nếu chưa có
        page = pages[0] if pages else await context.new_page()
            
        log_info("✅ Kết nối Chrome CDP thành công!")
        return browser, context, page
        
    except Exception as e:
        log_error(f"X Lỗi kết nối Chrome CDP ({cdp_url}): {str(e)}")
        log_warning("⚠️ Hãy đảm bảo bạn đã mở Chrome bằng file login_setup.py hoặc lệnh mở CDP Port 9222 trước!")
        return None, None, None

async def close_cdp(browser: Browser):
    """
    Ngắt kết nối Playwright khỏi Chrome (không đóng cửa sổ Chrome của người dùng).
    """
    global _playwright_instance
    try:
        if browser:
            await browser.close()
            log_info("🔌 Đã ngắt kết nối CDP an toàn.")
        if _playwright_instance:
            await _playwright_instance.stop()
            _playwright_instance = None
    except Exception as e:
        log_warning(f"Lỗi khi đóng kết nối CDP: {str(e)}")