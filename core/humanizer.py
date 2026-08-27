import math
import random
import time
from playwright.sync_api import Page
from utils.logger import get_logger

logger = get_logger("Humanizer")


class Humanizer:
    """Mô phỏng hành vi thao tác của người dùng thật trên Facebook."""

    # Bản đồ các phím gần nhau trên bàn phím QWERTY để giả lập gõ sai
    TYPO_MAP = {
        'a': ['s', 'q', 'w', 'z'], 'b': ['v', 'g', 'h', 'n'], 'c': ['x', 'd', 'v'],
        'd': ['s', 'e', 'r', 'f', 'c', 'x'], 'e': ['w', 's', 'd', 'r'],
        'f': ['d', 'r', 't', 'g', 'v', 'c'], 'g': ['f', 't', 'y', 'h', 'b', 'v'],
        'h': ['g', 'y', 'u', 'j', 'n', 'b'], 'i': ['u', 'j', 'k', 'o'],
        'k': ['j', 'i', 'o', 'l'], 'l': ['k', 'o', 'p'], 'm': ['n', 'j', 'k'],
        'n': ['b', 'h', 'j', 'm'], 'o': ['i', 'k', 'l', 'p'], 'p': ['o', 'l'],
        'q': ['1', '2', 'w', 'a'], 'r': ['e', 'f', 't', '4'], 's': ['a', 'w', 'e', 'd', 'z', 'x'],
        't': ['r', 'g', 'y', '5'], 'u': ['y', 'h', 'j', 'i', '7'], 'v': ['c', 'f', 'g', 'b'],
        'w': ['q', 'a', 's', 'e', '3'], 'x': ['z', 's', 'd', 'c'], 'y': ['t', 'g', 'h', 'u', '6'],
        'z': ['a', 's', 'x']
    }

    @staticmethod
    def _lognormal_delay(mean_ms: float = 90.0, sigma: float = 0.4) -> float:
        """Tạo độ trễ theo phân phối Log-normal (tính bằng giây)."""
        mu = math.log(mean_ms / 1000.0)
        return max(0.02, random.lognormvariate(mu, sigma))

    @classmethod
    def human_type(
        cls,
        page: Page,
        selector: str,
        text: str,
        typo_rate: float = 0.03
    ) -> None:
        """Gõ văn bản với nhịp Log-normal và tự động sửa nếu gõ sai nhầm phím."""
        element = page.locator(selector).first
        element.click()
        time.sleep(random.uniform(0.3, 0.7))

        for char in text:
            # Giả lập gõ sai phím dựa trên tỷ lệ typo_rate (chỉ áp dụng cho chữ cái thường)
            if char.lower() in cls.TYPO_MAP and random.random() < typo_rate:
                wrong_char = random.choice(cls.TYPO_MAP[char.lower()])
                page.keyboard.press(wrong_char)
                time.sleep(cls._lognormal_delay(mean_ms=120))
                
                # Tạm dừng ngắn để "nhận ra" lỗi sai, sau đó Backspace để sửa
                time.sleep(random.uniform(0.2, 0.5))
                page.keyboard.press("Backspace")
                time.sleep(cls._lognormal_delay(mean_ms=80))

            # Gõ ký tự chính xác
            page.keyboard.press(char)

            # Phím cách hoặc dấu câu sẽ dừng lại lâu hơn một chút (nghĩ câu)
            if char in [' ', '.', ',', '!', '?', '\n']:
                delay = cls._lognormal_delay(mean_ms=180, sigma=0.5)
            else:
                delay = cls._lognormal_delay(mean_ms=85, sigma=0.35)

            time.sleep(delay)

        logger.info(f"Đã gõ xong đoạn văn bản ({len(text)} ký tự).")

    @classmethod
    def human_scroll(
        cls,
        page: Page,
        total_pixels: int = None,
        direction: str = "down"
    ) -> None:
        """Cuộn trang với gia tốc đường cong Cosine và hành vi nhích nhẹ ngẫu nhiên."""
        if total_pixels is None:
            total_pixels = random.randint(350, 750)

        if direction == "up":
            total_pixels = -abs(total_pixels)
        else:
            total_pixels = abs(total_pixels)

        steps = random.randint(12, 22)
        scrolled = 0

        for i in range(steps):
            # Tính toán gia tốc theo đường cong Cosine (chậm -> nhanh -> chậm dần)
            progress = (i + 1) / steps
            ease_factor = (1 - math.cos(progress * math.pi)) / 2
            
            target_step = int(total_pixels * ease_factor) - scrolled
            scrolled += target_step

            # Thực thi thao tác cuộn qua bánh xe chuột (Mouse Wheel Event)
            page.mouse.wheel(0, target_step)
            
            # Độ trễ vi mô giữa các bước cuộn
            time.sleep(random.uniform(0.015, 0.045))

        # 15% xác suất nhích chuột ngược lại một lượng nhỏ (giả lập đọc lại nội dung)
        if random.random() < 0.15:
            time.sleep(random.uniform(0.1, 0.3))
            back_step = -int(total_pixels * random.uniform(0.05, 0.12))
            page.mouse.wheel(0, back_step)

        logger.info(f"Đã cuộn trang {direction} {abs(scrolled)}px.")

    @classmethod
    def random_pause(cls, min_sec: float = 3.0, max_sec: float = 8.0) -> None:
        """Dừng nghỉ đọc nội dung theo phân phối ngẫu nhiên lệch trái."""
        pause_time = random.triangular(min_sec, max_sec, min_sec + (max_sec - min_sec) * 0.3)
        time.sleep(pause_time)