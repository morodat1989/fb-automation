import socket
import time
from playwright.sync_api import sync_playwright, Playwright, Browser, Page
from utils.logger import get_logger

logger = get_logger("BrowserManager")


class BrowserManager:
    """Quản lý kết nối Playwright tới Google Chrome qua cổng CDP 127.0.0.1:9222."""

    def __init__(self, cdp_port: int = 9222):
        self.cdp_port = cdp_port
        self.cdp_url = f"http://127.0.0.1:{cdp_port}"
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    def _is_port_open(self, host: str = "127.0.0.1", timeout: int = 2) -> bool:
        """Kiểm tra kết nối tới cổng Debugging của Chrome trước khi gọi Playwright."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, self.cdp_port)) == 0

    def connect(self) -> Page | None:
        """Kết nối Playwright vào cửa sổ Chrome đã mở sẵn."""
        if not self._is_port_open():
            logger.error(f"Cổng {self.cdp_port} chưa được mở! Chrome chưa khởi chạy.")
            logger.warning("Vui lòng khởi chạy Profile Chrome từ Menu [1] trước khi chọn chạy kịch bản.")
            return None

        try:
            logger.info(f"Đang kết nối tới Chrome qua CDP: {self.cdp_url}...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_url)

            contexts = self.browser.contexts
            if not contexts:
                logger.error("Không tìm thấy Context trình duyệt nào.")
                return None

            context = contexts[0]
            self.page = context.pages[0] if context.pages else context.new_page()

            logger.info("Kết nối CDP thành công!")
            return self.page

        except Exception as e:
            logger.error(f"Lỗi kết nối CDP tới {self.cdp_url}: {e}")
            self.close()
            return None

    def close(self) -> None:
        """Ngắt điều khiển của Playwright, giữ Chrome tiếp tục chạy trên màn hình."""
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass
        self.browser = None
        self.page = None
        logger.info("Đã giải phóng kết nối Playwright CDP (Chrome vẫn chạy bình thường).")