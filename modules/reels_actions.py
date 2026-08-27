import random
import time
from playwright.async_api import Page
from utils.logger import log_info, log_warning, log_error
from utils.selectors import REELS_SELECTORS
from core.humanizer import random_delay, human_type

async def run_reels_seeding(
    page: Page,
    total_reels: int = 10,
    comments_list: list = None,
    like_ratio: float = 0.35,
    comment_ratio: float = 0.15
):
    """
    Kịch bản lướt Reels, xem ngẫu nhiên, thả tim và comment tự nhiên.
    :param page: Playwright Page instance
    :param total_reels: Số lượng Reels sẽ xem trong phiên
    :param comments_list: Danh sách nội dung comment tiếng Việt
    :param like_ratio: Tỉ lệ thả tim (0.35 = 35%)
    :param comment_ratio: Tỉ lệ bình luận (0.15 = 15%)
    """
    if comments_list is None:
        comments_list = ["Hay quá bạn ơi", "Đúng cái mình đang tìm luôn", "Video xịn quá", "Thả tim nè ❤️", "Nội dung chất lượng ghê"]

    log_info(f"🚀 Bắt đầu kịch bản Seeding Reels (Mục tiêu: {total_reels} video)...")

    # Truy cập trực tiếp trang Facebook Reels
    try:
        await page.goto("https://www.facebook.com/reel/", wait_until="networkidle", timeout=30000)
        await random_delay(3, 5)
    except Exception as e:
        log_error(f"Không thể truy cập Facebook Reels: {str(e)}")
        return

    for i in range(1, total_reels + 1):
        log_info(f"--- 🎬 Đang xem Reel [{i}/{total_reels}] ---")
        
        # 1. Giả lập thời gian xem ngẫu nhiên (Watch time: 15s - 40s)
        watch_time = random.uniform(15, 40)
        log_info(f"⏱️ Giữ màn hình xem trong {watch_time:.1f} giây...")
        await page.wait_for_timeout(watch_time * 1000)

        # 2. Quyết định Thả tim (Chỉ thả tim nếu xem > 18s và trúng tỷ lệ)
        if watch_time > 18 and random.random() < like_ratio:
            await _action_like_reel(page)

        # 3. Quyết định Comment (Chỉ comment nếu xem > 22s và trúng tỷ lệ)
        if watch_time > 22 and random.random() < comment_ratio:
            comment_text = random.choice(comments_list)
            await _action_comment_reel(page, comment_text)

        # 4. Chuyển sang Reel tiếp theo bằng phím mũi tên xuống (ArrowDown)
        log_info("➡️ Chuyển sang Reel tiếp theo...")
        await page.keyboard.press("ArrowDown")
        await random_delay(2.5, 4.5)

    log_info("✅ Đã hoàn thành kịch bản Seeding Reels!")


async def _action_like_reel(page: Page):
    """Xử lý thả tim nút Thích của Reel hiện tại"""
    try:
        # Tìm nút Thích bằng aria-label hoặc selector tối ưu
        like_btn = page.locator(REELS_SELECTORS["like_btn"]).first
        if await like_btn.is_visible(timeout=3000):
            # Kiểm tra xem đã like chưa qua thuộc tính aria-pressed
            is_liked = await like_btn.get_attribute("aria-pressed")
            if is_liked != "true":
                await like_btn.click()
                log_info("❤️ Đã thả tim Reel!")
                await random_delay(1, 2)
            else:
                log_info("ℹ️ Reel này đã thả tim từ trước, bỏ qua.")
    except Exception as e:
        log_warning(f"Thả tim thất bại hoặc không tìm thấy nút: {str(e)}")


async def _action_comment_reel(page: Page, text: str):
    """Xử lý gửi bình luận trên Reel hiện tại"""
    try:
        # Mở hộp thoại comment nếu chưa hiển thị
        comment_icon = page.locator(REELS_SELECTORS["comment_icon"]).first
        if await comment_icon.is_visible(timeout=3000):
            await comment_icon.click()
            await random_delay(1.5, 3)

        # Tìm ô nhập bình luận
        comment_box = page.locator(REELS_SELECTORS["comment_box"]).first
        if await comment_box.is_visible(timeout=4000):
            await comment_box.click()
            await random_delay(0.8, 1.5)
            
            # Gõ văn bản tiếng Việt Unicode an toàn bằng clipboard/human_type
            await human_type(page, comment_box, text)
            await random_delay(1, 2)
            
            # Gửi bằng phím Enter
            await page.keyboard.press("Enter")
            log_info(f"💬 Đã comment: \"{text}\"")
            await random_delay(2, 4)
            
            # Đóng bảng comment nếu có nút close
            close_btn = page.locator(REELS_SELECTORS["close_comment_btn"]).first
            if await close_btn.is_visible(timeout=2000):
                await close_btn.click()
                await random_delay(1, 1.5)
    except Exception as e:
        log_warning(f"Bình luận Reels thất bại: {str(e)}")