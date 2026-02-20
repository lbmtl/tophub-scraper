"""
配置文件示例
复制此文件为 config.py 并根据需要修改
"""

# ============ 爬虫配置 ============

# 请求间隔范围（秒）
# 较小的值会加快爬取速度，但可能触发反爬
DELAY_RANGE = (2, 4)

# 最大重试次数
MAX_RETRIES = 3

# 请求超时（秒）
TIMEOUT = 30

# 代理池配置（可选）
# 格式: "http://user:pass@host:port" 或 "http://host:port"
PROXY_POOL = [
    # "http://127.0.0.1:7890",  # 示例：本地代理
    # "http://user:pass@proxy.example.com:8080",
]

# ============ Edge 浏览器配置 ============

# 是否使用无头模式（不显示浏览器窗口）
HEADLESS = True

# 浏览器窗口大小
WINDOW_SIZE = (1920, 1080)

# 页面加载超时（毫秒）
PAGE_TIMEOUT = 30000

# Edge 用户数据目录（保持登录状态，可选）
# 设为 None 使用临时目录
USER_DATA_DIR = None  # r"C:\Users\YourName\AppData\Local\Microsoft\Edge\User Data"

# ============ 输出配置 ============

# 默认输出目录
OUTPUT_DIR = "./output"

# 是否保存到桌面
SAVE_TO_DESKTOP = False

# ============ 定时任务配置 ============

# 定时执行间隔（小时）
SCHEDULE_INTERVAL = 2

# 日志目录
LOG_DIR = "./logs"

# ============ 反爬策略 ============

# User-Agent 轮换列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# 是否启用随机 User-Agent
RANDOM_UA = True
