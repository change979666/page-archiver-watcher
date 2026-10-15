"""
配置文件
"""

# 归档设置
ARCHIVE_DIR = "archived_pages"  # 归档文件保存目录
ARCHIVE_URLS_FILE = "archived_urls.json"  # 已归档URL记录文件

# 浏览器设置
BROWSER_HEADLESS = False  # 是否使用无头模式
BROWSER_TIMEOUT = 30000  # 页面加载超时时间（毫秒）

# 白名单设置（可选）
WHITELIST_DOMAINS = [
    "tiktok.com",
    "douyin.com"
]

# 归档设置
MAX_ARCHIVE_SIZE = 1000  # 最大归档数量
ARCHIVE_INTERVAL = 1  # 归档间隔（秒） 