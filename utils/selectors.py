# Quản lý tập trung toàn bộ Facebook Selectors

FEED_SELECTORS = {
    "like_btn": 'div[role="button"][aria-label="Thích"], div[role="button"][aria-label="Like"]',
    "comment_box": 'div[role="textbox"][aria-label="Viết bình luận..."], div[role="textbox"][aria-label="Write a comment..."]'
}

REELS_SELECTORS = {
    "like_btn": 'div[aria-label="Thích"], div[aria-label="Like"]',
    "comment_icon": 'div[aria-label="Bình luận"], div[aria-label="Comment"]',
    "comment_box": 'div[aria-label="Viết bình luận..."], div[aria-label="Write a comment..."], div[role="textbox"]',
    "close_comment_btn": 'div[aria-label="Đóng"], div[aria-label="Close"]'
}

DIRECT_POST_SELECTORS = {
    "unavailable_text": [
        "Nội dung này hiện không hiển thị",
        "This content isn't available right now",
        "Trang này không có sẵn",
        "This page isn't available"
    ],
    "like_btn": 'div[role="button"][aria-label="Thích"], div[role="button"][aria-label="Like"]',
    "comment_box": 'div[role="textbox"][aria-label="Viết bình luận..."], div[role="textbox"][aria-label="Write a comment..."], div[role="textbox"][aria-label="Viết bình luận công khai..."]'
}