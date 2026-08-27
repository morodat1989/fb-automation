import random
import time
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from core.humanizer import Humanizer
from utils.selectors import FBSelectors
from utils.logger import get_logger

logger = get_logger("FeedActions")


class FeedActions:
    """Quản lý các hành vi lướt tin tức, thả cảm xúc và bình luận trên Facebook Newsfeed."""

    def __init__(self, page: Page):
        self.page = page
        self.processed_posts = set()  # Lưu vết bài viết đã tương tác trong phiên để tránh trùng lặp

    def ensure_newsfeed(self) -> bool:
        """Kiểm tra và chuyển hướng về trang chủ Newsfeed nếu cần."""
        try:
            if "facebook.com" not in self.page.url:
                self.page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
                Humanizer.random_pause(3.0, 5.0)

            self.page.wait_for_selector(FBSelectors.MAIN_FEED, timeout=12000)
            return True
        except PlaywrightTimeoutError:
            logger.warning("Không tìm thấy vùng hiển thị Feed chính trên màn hình.")
            return False

    def browse_and_interact(
        self,
        scroll_count: int = 8,
        like_prob: float = 0.35,
        comment_prob: float = 0.15,
        comments_list: list[str] | None = None
    ) -> None:
        """
        Lướt Newsfeed và tương tác ngẫu nhiên bài viết.

        :param scroll_count: Số lần thực hiện cuộn trang.
        :param like_prob: Xác suất thả cảm xúc (0.0 - 1.0).
        :param comment_prob: Xác suất bình luận (0.0 - 1.0).
        :param comments_list: Danh sách các mẫu câu bình luận ngẫu nhiên.
        """
        if not self.ensure_newsfeed():
            logger.error("Dừng kịch bản do không truy cập được Newsfeed.")
            return

        if comments_list is None:
            comments_list = [
                "Bài viết rất hay!",
                "Thông tin bổ ích quá ạ",
                "Tuyệt vời quá anh/chị",
                "Up lên cho mọi người cùng thấy",
                "Quan tâm ạ"
            ]

        logger.info(f"Bắt đầu lướt Newsfeed ({scroll_count} lượt cuộn)...")

        for i in range(1, scroll_count + 1):
            logger.info(f"--- Lượt cuộn {i}/{scroll_count} ---")

            # Cuộn trang ngẫu nhiên bằng gia tốc đường cong Cosine
            Humanizer.human_scroll(self.page, direction="down")

            # Dừng lại giả lập đọc nội dung
            Humanizer.random_pause(4.0, 9.0)

            # Quét danh sách bài viết đang hiển thị trên giao diện
            posts = self.page.locator(FBSelectors.POST_CONTAINER).all()
            if not posts:
                continue

            # Chọn bài viết mới nhất chưa tương tác trong phiên chạy
            target_post = None
            for post in reversed(posts):
                try:
                    # Tạo ID nhận diện ngắn dựa trên thuộc tính hoặc văn bản đầu bài viết
                    post_identifier = post.evaluate(
                        "el => el.getAttribute('aria-describedby') || el.innerText.slice(0, 60)"
                    )
                    if post_identifier not in self.processed_posts:
                        target_post = post
                        self.processed_posts.add(post_identifier)
                        break
                except Exception:
                    continue

            if not target_post:
                target_post = posts[-1]

            # 1. Thả Like ngẫu nhiên theo xác suất
            if random.random() < like_prob:
                self.react_to_post(target_post)

            # 2. Bình luận ngẫu nhiên theo xác suất
            if random.random() < comment_prob and comments_list:
                selected_comment = random.choice(comments_list)
                self.comment_on_post(target_post, selected_comment)

        logger.info("Hoàn tất kịch bản tương tác Newsfeed.")

    def react_to_post(self, post_locator) -> bool:
        """Thả cảm xúc cho bài viết được chỉ định."""
        try:
            like_btn = post_locator.locator(FBSelectors.LIKE_BUTTON).first
            if like_btn.is_visible():
                like_btn.scroll_into_view_if_needed()
                time.sleep(random.uniform(0.3, 0.7))

                # Kiểm tra trạng thái bài viết đã Like chưa để tránh huỷ Like (Unlike)
                is_pressed = like_btn.get_attribute("aria-pressed")
                aria_label = like_btn.get_attribute("aria-label") or ""

                if is_pressed == "true" or "Bỏ thích" in aria_label or "Unlike" in aria_label:
                    logger.info("Bài viết đã được thích từ trước, bỏ qua.")
                    return False

                # Di chuột đến nút bấm trước khi click
                like_btn.hover()
                time.sleep(random.uniform(0.2, 0.4))
                like_btn.click()

                logger.info("Đã bấm Thích bài viết thành công.")
                Humanizer.random_pause(1.5, 3.0)
                return True
        except Exception as e:
            logger.debug(f"Thao tác bấm Like không thành công: {e}")
        return False

    def comment_on_post(self, post_locator, text: str) -> bool:
        """Gửi bình luận vào bài viết được chỉ định."""
        try:
            comment_input = post_locator.locator(FBSelectors.COMMENT_INPUT).first
            if comment_input.is_visible():
                comment_input.scroll_into_view_if_needed()
                time.sleep(random.uniform(0.5, 1.0))

                # Kích hoạt ô nhập bình luận
                comment_input.click()
                time.sleep(random.uniform(0.4, 0.8))

                # SỬA LỖI: Dùng keyboard.type để gõ ký tự Tiếng Việt / Unicode chuẩn
                # Tránh lỗi Unknown Key của Playwright khi dùng keyboard.press("á", "ơ",...)
                for char in text:
                    self.page.keyboard.type(char, delay=random.randint(50, 150))

                time.sleep(random.uniform(0.8, 1.5))
                self.page.keyboard.press("Enter")

                logger.info(f"Đã đăng bình luận: '{text}'")
                Humanizer.random_pause(3.0, 6.0)
                return True
        except Exception as e:
            logger.debug(f"Thao tác bình luận không thành công: {e}")
        return False