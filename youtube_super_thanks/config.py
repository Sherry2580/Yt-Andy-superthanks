DATABASE_FILE = 'super_thanks.db'

# 瀏覽器設定
BROWSER_SETTINGS = {
    "disable_notifications": True,
    "disable_images": True,
    "disable_extensions": True,
    "page_load_strategy": 'eager',
    "headless": True
}

SCROLL_SETTINGS = {
    "max_scrolls": 60,  # 最大滾動次數
    "scroll_pause_time": 5,  # 每次滾動的暫停時間
    "no_change_threshold": 5  # 連續幾次沒變化就停止
}

DEFAULT_EXCHANGE_RATES = {
    '$': 1.0,           # 新台幣
    'US$': 32.95,       # 美元
    'HK$': 4.213,       # 港幣
    'SGD': 24.65,       # 新加坡元
    'CA$': 22.87,       # 加拿大元
    'MYR': 7.35,        # 馬來西亞令吉
    '¥': 0.22,          # 日元
    'AU$': 20.78,       # 澳元
    '£': 42.48,         # 英鎊
    '€': 35.7,          # 歐元
    'NZ$': 18.85,       # 紐西蘭元
    'PHP': 0.55,        # 菲律賓比索
    'THB': 0.96,        # 泰銖
    'IDR': 0.0020,      # 印尼盾
    'TRY': 0.97,        # 土耳其里拉
    'CLP': 0.035,       # 智利比索
    'ARS': 0.035,       # 阿根廷比索
    'AED': 8.59,        # 阿聯酋迪拉姆
}

CSS_SELECTORS = {
    "super_thanks": "#comment-chip-price",
    "commenter_name": "#author-text span",
    "comment_text": "ytd-comment-renderer #content-text",
    "video_title": "yt-formatted-string.ytd-watch-metadata[title]",
    "channel_name": "#channel-name #text",
    "comments": "ytd-comment-thread-renderer"
}