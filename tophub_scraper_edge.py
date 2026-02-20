#!/usr/bin/env python3
"""
今日热榜爬虫 - Edge浏览器版 (Playwright)
https://tophub.today/c/news

特性:
- 使用 Microsoft Edge 浏览器渲染页面
- 绕过反爬检测（真实浏览器环境）
- 支持无头/有头模式
- 自动等待页面加载完成
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class HotItem:
    """热榜条目数据结构"""
    platform: str
    ranking: int
    title: str
    url: str
    heat: Optional[str]
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "platform": self.platform,
            "ranking": self.ranking,
            "title": self.title,
            "url": self.url,
            "heat": self.heat,
            "timestamp": self.timestamp
        }


class TopHubEdgeScraper:
    """今日热榜 Edge 浏览器爬虫"""
    
    BASE_URL = "https://tophub.today/c/news"
    
    def __init__(
        self,
        headless: bool = True,
        window_size: tuple = (1920, 1080),
        timeout: int = 30000,
        user_data_dir: Optional[str] = None
    ):
        """
        初始化爬虫
        
        Args:
            headless: 是否无头模式（不显示浏览器窗口）
            window_size: 浏览器窗口大小
            timeout: 页面加载超时（毫秒）
            user_data_dir: Edge 用户数据目录（保持登录状态）
        """
        self.headless = headless
        self.window_size = window_size
        self.timeout = timeout
        self.user_data_dir = user_data_dir
        self.browser: Optional[Browser] = None
        self.context = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.playwright = await async_playwright().start()
        
        # 尝试启动 Edge 浏览器
        # Edge 通常在以下路径
        edge_paths = [
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",  # macOS
            "/usr/bin/microsoft-edge",  # Linux
        ]
        
        executable_path = None
        for path in edge_paths:
            if os.path.exists(path):
                executable_path = path
                logger.info(f"找到 Edge 浏览器: {path}")
                break
        
        if not executable_path:
            logger.warning("未找到 Edge 浏览器，将使用 Chromium")
        
        # 启动浏览器
        browser_kwargs = {
            "headless": self.headless,
            "args": [
                f"--window-size={self.window_size[0]},{self.window_size[1]}",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        }
        
        if executable_path:
            browser_kwargs["executable_path"] = executable_path
        
        if self.user_data_dir:
            browser_kwargs["user_data_dir"] = self.user_data_dir
            
        self.browser = await self.playwright.chromium.launch(**browser_kwargs)
        
        # 创建新上下文
        self.context = await self.browser.new_context(
            viewport={"width": self.window_size[0], "height": self.window_size[1]},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.0 Edg/120.0.0.0"
        )
        
        # 注入脚本绕过 webdriver 检测
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def _scroll_to_load(self, page: Page):
        """滚动页面加载所有内容"""
        logger.info("滚动页面加载内容...")
        
        # 获取初始高度
        last_height = await page.evaluate("document.body.scrollHeight")
        
        while True:
            # 滚动到底部
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            
            # 等待新内容加载
            await page.wait_for_load_state("networkidle")
            
            # 检查是否还有更多内容
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
        logger.info("页面滚动完成")
    
    async def scrape(self) -> List[HotItem]:
        """执行爬取任务"""
        logger.info(f"开始爬取: {self.BASE_URL}")
        
        page = await self.context.new_page()
        
        try:
            # 访问页面
            logger.info("正在加载页面...")
            await page.goto(self.BASE_URL, wait_until="networkidle", timeout=self.timeout)
            
            # 等待内容加载
            await page.wait_for_selector('div[class^="cc-cd"]', timeout=self.timeout)
            
            # 滚动加载更多内容
            await self._scroll_to_load(page)
            
            # 提取数据
            items = await self._extract_data(page)
            
            logger.info(f"成功获取 {len(items)} 条数据")
            return items
            
        finally:
            await page.close()
    
    async def _extract_data(self, page: Page) -> List[HotItem]:
        """从页面提取数据"""
        items = []
        timestamp = datetime.now().isoformat()
        
        # 获取所有平台容器
        containers = await page.query_selector_all('div[class^="cc-cd"]')
        logger.info(f"发现 {len(containers)} 个平台榜单")
        
        for container in containers:
            try:
                # 提取平台名称
                platform_elem = await container.query_selector('.cc-cd-lb, [class*="lb"]')
                platform = await platform_elem.inner_text() if platform_elem else "未知平台"
                platform = platform.strip()
                
                # 获取该平台下的所有条目
                item_elements = await container.query_selector_all('div[class^="cc-cd-cb"] a, div.cc-cd-cb a')
                
                for idx, elem in enumerate(item_elements, 1):
                    try:
                        # 提取标题
                        title = await elem.inner_text()
                        title = title.strip()
                        if not title:
                            continue
                        
                        # 提取链接
                        href = await elem.get_attribute('href') or ""
                        if href and not href.startswith('http'):
                            href = 'https://tophub.today' + href
                        
                        # 提取热度（从相邻元素）
                        heat = None
                        # 尝试多种方式获取热度
                        heat_elem = await elem.query_selector('xpath=following-sibling::*[1]')
                        if heat_elem:
                            heat_text = await heat_elem.inner_text()
                            if any(c in heat_text for c in '0123456789'):
                                heat = heat_text.strip()
                        
                        item = HotItem(
                            platform=platform,
                            ranking=idx,
                            title=title,
                            url=href,
                            heat=heat,
                            timestamp=timestamp
                        )
                        items.append(item)
                        
                    except Exception as e:
                        logger.warning(f"解析条目时出错: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"解析平台容器时出错: {e}")
                continue
        
        return items
    
    def save_to_json(self, items: List[HotItem], filepath: str):
        """保存数据到 JSON 文件"""
        data = [item.to_dict() for item in items]
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存到: {filepath}")
    
    def save_to_csv(self, items: List[HotItem], filepath: str):
        """保存数据到 CSV 文件"""
        import csv
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['平台', '排名', '标题', '链接', '热度', '时间戳'])
            
            for item in items:
                writer.writerow([
                    item.platform,
                    item.ranking,
                    item.title,
                    item.url,
                    item.heat,
                    item.timestamp
                ])
        logger.info(f"数据已保存到: {filepath}")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='今日热榜 Edge 浏览器爬虫')
    parser.add_argument('--headless', action='store_true', default=True, 
                        help='无头模式（默认开启）')
    parser.add_argument('--no-headless', action='store_true',
                        help='显示浏览器窗口')
    parser.add_argument('--output', '-o', default='output',
                        help='输出目录')
    parser.add_argument('--wait', '-w', type=int, default=30000,
                        help='页面加载超时（毫秒，默认30000）')
    
    args = parser.parse_args()
    headless = not args.no_headless
    
    async with TopHubEdgeScraper(
        headless=headless,
        timeout=args.wait
    ) as scraper:
        items = await scraper.scrape()
        
        if items:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(args.output)
            output_dir.mkdir(exist_ok=True)
            
            json_file = output_dir / f"tophub_{timestamp}.json"
            csv_file = output_dir / f"tophub_{timestamp}.csv"
            
            scraper.save_to_json(items, str(json_file))
            scraper.save_to_csv(items, str(csv_file))
            
            # 打印预览
            print("\n=== 数据预览 (前10条) ===")
            for item in items[:10]:
                heat_str = f" (热度: {item.heat})" if item.heat else ""
                print(f"[{item.platform}] #{item.ranking} {item.title[:50]}...{heat_str}")
            
            print(f"\n共获取 {len(items)} 条数据")
            print(f"JSON: {json_file}")
            print(f"CSV: {csv_file}")
        else:
            print("未获取到数据")


if __name__ == "__main__":
    asyncio.run(main())
