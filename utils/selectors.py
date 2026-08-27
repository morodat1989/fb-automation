class FBSelectors:
    # --- Trạng thái chung ---
    MAIN_FEED = '[role="main"]'
    ACCOUNT_MENU = '[aria-label="Your profile"], [aria-label="Tài khoản của bạn"]'
    
    # --- Newsfeed & Bài viết ---
    POST_CONTAINER = '[role="feed"] > div, [data-pagelet="FeedUnit"]'
    LIKE_BUTTON = '[aria-label="Like"], [aria-label="Thích"]'
    COMMENT_INPUT = '[role="textbox"][aria-label*="Write a comment"], [role="textbox"][aria-label*="Viết bình luận"]'
    
    # --- Khung soạn bài ---
    CREATE_POST_BOX = '[role="button"]:has-text("What\'s on your mind"), [role="button"]:has-text("Bạn đang nghĩ gì")'
    POST_TEXTAREA = '[role="textbox"][aria-label*="What\'s on your mind"], [role="textbox"][aria-label*="Bạn đang nghĩ gì"]'
    SUBMIT_POST_BTN = '[aria-label="Post"], [aria-label="Đăng"]'
    
    # --- REELS_SELECTORS ---
    REELS_SELECTORS = {
    "like_btn": 'div[aria-label="Thích"], div[aria-label="Like"]',
    "comment_icon": 'div[aria-label="Bình luận"], div[aria-label="Comment"]',
    "comment_box": 'div[aria-label="Viết bình luận..."], div[aria-label="Write a comment..."], div[role="textbox"]',
    "close_comment_btn": 'div[aria-label="Đóng"], div[aria-label="Close"]'
}