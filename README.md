# 今日热榜爬虫 | TopHub Scraper

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Playwright](https://img.shields.io/badge/Playwright-Edge-orange)](https://playwright.dev/)

使用 Microsoft Edge 浏览器爬取 [今日热榜](https://tophub.today) 数据的 Python 工具，支持多平台热榜聚合。

## ✨ 特性

- 🔥 **多平台支持** - 知乎、微博、微信、百度、抖音、B站等热门平台
- 🌐 **Edge 浏览器** - 使用 Playwright 驱动真实 Edge 浏览器，绕过反爬
- 🔄 **双模式运行** - 支持 HTTP 请求模式 和 浏览器渲染模式
- 📊 **多格式输出** - JSON、CSV 格式保存
- ⏰ **定时任务** - 内置调度器支持定时爬取
- 🪟 **Windows 服务** - 可部署为 Windows 后台服务

## 📦 安装

### 1. 克隆仓库

```bash
git clone https://github.com/lbmtl/tophub-scraper.git
cd tophub-scraper
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器

```bash
playwright install chromium
```

## 🚀 快速开始

### 方式 1: Edge 浏览器模式（推荐）

使用真实 Edge 浏览器渲染页面，绕过反爬检测：

```bash
python tophub_scraper_edge.py
```

显示浏览器窗口（调试用）：
```bash
python tophub_scraper_edge.py --no-headless
```

### 方式 2: HTTP 请求模式

轻量级模式，适合快速抓取：

```bash
python tophub_scraper.py
```

## 📖 使用示例

### 命令行参数

```bash
# Edge 模式 - 自定义输出目录
python tophub_scraper_edge.py --output ./data --wait 60000

# HTTP 模式 - 使用代理
python tophub_scraper.py
```

### Python API

```python
import asyncio
from tophub_scraper_edge import TopHubEdgeScraper

async def main():
    async with TopHubEdgeScraper(headless=True) as scraper:
        items = await scraper.scrape()
        
        # 保存数据
        scraper.save_to_json(items, "data.json")
        scraper.save_to_csv(items, "data.csv")
        
        for item in items[:5]:
            print(f"[{item.platform}] {item.title}")

asyncio.run(main())
```

## 📂 项目结构

```
tophub-scraper/
├── tophub_scraper.py           # HTTP 请求模式
├── tophub_scraper_edge.py      # Edge 浏览器模式
├── tophub_service.py           # 定时服务
├── requirements.txt            # 依赖
├── config.py                   # 配置文件（可选）
├── README.md
├── LICENSE
└── .github/
    └── workflows/
        └── ci.yml              # CI 配置
```

## ⚙️ 配置说明

### Edge 浏览器路径

程序会自动检测 Edge 安装位置。如需手动指定：

```python
# 在 TopHubEdgeScraper 初始化时传入
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
```

### 代理设置

**HTTP 模式：**
```python
proxy_pool = [
    "http://user:pass@host:port",
    "http://host:port",
    "socks5://host:port",
]
scraper = TopHubScraper(proxy_pool=proxy_pool)
```

**Edge 模式：**
```python
# 通过 playwright 的代理参数
browser = await playwright.chromium.launch(
    proxy={"server": "http://proxy.example.com:8080"}
)
```

## 🖥️ 部署为 Windows 服务

```bash
# 安装服务（管理员权限）
python tophub_service.py install
python tophub_service.py start

# 管理服务
python tophub_service.py stop
python tophub_service.py restart
python tophub_service.py remove
```

## 📊 输出格式

### JSON 示例

```json
[
  {
    "platform": "知乎",
    "ranking": 1,
    "title": "如何看待xxx事件",
    "url": "https://tophub.today/...",
    "heat": "644万",
    "timestamp": "2026-02-20T09:30:00"
  }
]
```

### CSV 格式

| 平台 | 排名 | 标题 | 链接 | 热度 | 时间戳 |
|------|------|------|------|------|--------|
| 知乎 | 1 | 如何看待... | https://... | 644万 | 2026-02-20T09:30:00 |

## ⚠️ 免责声明

1. 本工具仅供学习研究使用
2. 请遵守 [今日热榜](https://tophub.today) 的 robots.txt 和爬虫协议
3. 控制爬取频率，避免对服务器造成压力
4. 商业使用请获得目标网站授权

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 🙏 致谢

- [今日热榜](https://tophub.today) - 数据来源
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML 解析

---

Made with ❤️ by lbmtl
