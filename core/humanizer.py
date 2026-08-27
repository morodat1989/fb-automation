import math
import random
import asyncio
from playwright.async_api import Page, Locator
from utils.logger import log_debug

async def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """Tạo khoảng nghỉ ngẫu nhiên giữa min_seconds và max_seconds"""
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)

async def human_type(page: Page, locator: Locator, text: str):
    """
    Nhập văn bản giả lập hành vi gõ phím người thật.
    Hỗ trợ bảo toàn Unicode tiếng Việt.
    """
    try:
        # Gõ từng ký tự với độ trễ ngẫu nhiên
        for char in text:
            await locator.type(char, delay=random.randint(60, 140))
    except Exception:
        # Fallback an toàn nếu gõ từng phím bị mất dấu tiếng Việt
        await locator.fill(text)

async def smooth_scroll(page: Page, distance: int = 500, steps: int = 10):
    """
    Cuộn trang mượt mà giả lập hành vi lăn chuột (Cosine smoothing)
    """
    step_distance = distance / steps
    for i in range(steps):
        progress = (i + 1) / steps
        ease_factor = (1 - math.cos(progress * math.pi)) / 2
        current_step = step_distance * (0.8 + ease_factor * 0.4)
        
        await page.mouse.wheel(0, current_step)
        await asyncio.sleep(random.uniform(0.04, 0.12))

class Humanizer:
    """Class tương thích ngược cho các module cũ gọi dạng OOP"""
    def __init__(self, page: Page = None):
        self.page = page

    async def delay(self, min_s: float = 1.0, max_s: float = 3.0):
        await random_delay(min_s, max_s)

    async def scroll(self, distance: int = 500):
        if self.page:
            await smooth_scroll(self.page, distance)

    async def type_text(self, locator: Locator, text: str):
        if self.page:
            await human_type(self.page, locator, text)