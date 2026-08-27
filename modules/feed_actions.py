import random
import asyncio
from playwright.async_api import Page
from utils.logger import log_info, log_warning, log_error
from core.humanizer import random_delay, human_type, smooth_scroll

async def run_feed_seeding(
    page: Page,
    scroll_count: int = 5,
    comments_list: list = None,
    like_ratio: float = 0.4,
    comment_ratio: float = 0.2
):
    """
    Kịch bản lướt Newsfeed, tự động Like và Comment ngẫu nhiên bài viết.
    """
    if comments_list is None:
        comments_list = [
            "Bài viết hữu ích quá!",
            "Quan tâm ạ",
            "Tuyệt vời quá ad ơi",
            "Cảm ơn đã chia sẻ",
            "Chấm hóng thông tin ạ"
        ]

    log_info(f"🚀 Bắt đầu kịch bản Seeding Newsfeed ({scroll_count} lần cuộn)...")

    try:
        await page.goto("https://www.facebook.com/", wait_until="networkidle", timeout=30000)
        await random_delay(3, 5)
    except Exception as e:
        log_error(f"Không thể truy cập Facebook Home: {str(e)}")
        return

    for i in range(1, scroll_count + 1):
        log_info(f"--- 📜 [Lần cuộn {i}/{scroll_count}] ---")
        
        # Cuộn trang giả lập người dùng
        await smooth_scroll(page, distance=random.randint(300, 600))
        await random_delay(2, 4)

        # Thích ngẫu nhiên
        if random.random() < like_ratio:
            await _action_like_feed(page)

        # Comment ngẫu nhiên
        if random.random() < comment_ratio:
            comment_text = random.choice(comments_list)
            await _action_comment_feed(page, comment_text)

        await random_delay(2, 5)

    log_info("✅ Đã hoàn thành kịch bản Seeding Newsfeed!")


async def _action_like_feed(page: Page):
    """Thích bài viết trên Newsfeed"""
    try:
        like_btns = page.locator('div[role="button"][aria-label="Thích"], div[role="button"][aria-label="Like"]')
        count = await like_btns.count()
        if count > 0:
            for idx in range(count):
                btn = like_btns.nth(idx)
                if await btn.is_visible() and await btn.get_attribute("aria-pressed") != "true":
                    await btn.click()
                    log_info("👍 Đã Thích một bài viết trên Newsfeed!")
                    await random_delay(1, 2)
                    break
    except Exception as e:
        log_warning(f"Lỗi khi Like trên Newsfeed: {str(e)}")


async def _action_comment_feed(page: Page, text: str):
    """Bình luận bài viết trên Newsfeed"""
    try:
        comment_boxes = page.locator('div[role="textbox"][aria-label="Viết bình luận..."], div[role="textbox"][aria-label="Write a comment..."]')
        count = await comment_boxes.count()
        if count > 0:
            for idx in range(count):
                box = comment_boxes.nth(idx)
                if await box.is_visible():
                    await box.click()
                    await random_delay(0.8, 1.5)
                    await human_type(page, box, text)
                    await random_delay(1, 2)
                    await page.keyboard.press("Enter")
                    log_info(f"💬 Đã comment trên Newsfeed: \"{text}\"")
                    await random_delay(2, 4)
                    break
    except Exception as e:
        log_warning(f"Lỗi khi Comment trên Newsfeed: {str(e)}")