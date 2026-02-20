#!/usr/bin/env python3
"""
今日热榜爬虫 - TopHub.today Scraper
https://tophub.today/c/news

特性:
- 多平台榜单聚合(知乎、微博、微信、百度等)
- 智能反爬策略(请求头模拟、频率控制、指数退避)
- 代理池支持
- 结构化数据输出
"""

import time
import random
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import json

import requests
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class HotItem:
    """热榜条目数据结构"""
    platform: str           # 平台名称
    ranking: int           # 排名
    title: str             # 标题
    url: str               # 链接
    heat: Optional[int]    # 热度值
    timestamp: str         # 爬取时间
    
    def to_dict(self) -> Dict:
        return {
            "platform": self.platform,
            "ranking": self.ranking,
            "title": self.title,
            "url": self.url,
            "heat": self.heat,
            "timestamp": self.timestamp
        }


class TopHubScraper:
    """今日热榜爬虫类"""
    
    BASE_URL = "https://tophub.today/c/news"
    
    # 请求头模板
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://tophub.today/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0"
    }
    
    def __init__(
        self,
        delay_range: tuple = (2, 3),      # 请求间隔范围(秒)
        max_retries: int = 3,              # 最大重试次数
        proxy_pool: Optional[List[str]] = None,  # 代理池
        timeout: int = 30                  # 请求超时
    ):
        self.delay_range = delay_range
        self.max_retries = max_retries
        self.proxy_pool = proxy_pool or []
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.proxy_index = 0
        
    def _get_proxy(self) -> Optional[Dict[str, str]]:
        """获取下一个代理"""
        if not self.proxy_pool:
            return None
        proxy_url = self.proxy_pool[self.proxy_index % len(self.proxy_pool)]
        self.proxy_index += 1
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    
    def _exponential_backoff(self, attempt: int) -> float:
        """指数退避算法"""
        base_delay = 2 ** attempt
        jitter = random.uniform(0, 1)
        return base_delay + jitter
    
    def _make_request(self, url: str) -> Optional[str]:
        """发送HTTP请求，包含重试和退避逻辑"""
        for attempt in range(self.max_retries):
            try:
                # 请求间隔
                delay = random.uniform(*self.delay_range)
                logger.info(f"等待 {delay:.2f} 秒后请求...")
                time.sleep(delay)
                
                # 获取代理
                proxies = self._get_proxy()
                if proxies:
                    logger.info(f"使用代理: {proxies['http']}")
                
                # 发送请求
                response = self.session.get(
                    url,
                    proxies=proxies,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                # 处理429状态码
                if response.status_code == 429:
                    backoff_time = self._exponential_backoff(attempt)
                    logger.warning(f"触发频率限制(429)，退避 {backoff_time:.2f} 秒后重试...")
                    time.sleep(backoff_time)
                    continue
                
                # 检查状态码
                response.raise_for_status()
                
                logger.info(f"成功获取页面: {url}")
                return response.text
                
            except requests.exceptions.ProxyError as e:
                logger.error(f"代理错误: {e}")
                if attempt < self.max_retries - 1:
                    continue
                    
            except requests.exceptions.Timeout as e:
                logger.error(f"请求超时: {e}")
                if attempt < self.max_retries - 1:
                    backoff_time = self._exponential_backoff(attempt)
                    logger.info(f"退避 {backoff_time:.2f} 秒后重试...")
                    time.sleep(backoff_time)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常: {e}")
                if attempt < self.max_retries - 1:
                    backoff_time = self._exponential_backoff(attempt)
                    time.sleep(backoff_time)
                    
        logger.error(f"达到最大重试次数，请求失败: {url}")
        return None
    
    def _parse_heat_value(self, heat_text: str) -> Optional[int]:
        """解析热度值文本为数字"""
        if not heat_text:
            return None
        
        # 移除空白字符
        heat_text = heat_text.strip()
        
        # 匹配数字部分
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', heat_text)
        if not match:
            return None
        
        number = float(match.group(1))
        
        # 处理单位
        if '万' in heat_text:
            number *= 10000
        elif '亿' in heat_text:
            number *= 100000000
            
        return int(number)
    
    def _extract_platform_name(self, soup_element) -> str:
        """提取平台名称"""
        # 尝试多种选择器定位平台名称
        selectors = [
            '.cc-cd-lb',
            '.cc-cd-lb span',
            '[class*="lb"]'
        ]
        
        for selector in selectors:
            elem = soup_element.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        
        return "未知平台"
    
    def parse_page(self, html: str) -> List[HotItem]:
        """解析页面HTML，提取热榜数据"""
        items = []
        soup = BeautifulSoup(html, 'lxml')
        
        # 查找所有榜单容器
        platform_containers = soup.select('div[class^="cc-cd"]')
        logger.info(f"发现 {len(platform_containers)} 个平台榜单")
        
        for container in platform_containers:
            try:
                # 提取平台名称
                platform = self._extract_platform_name(container)
                
                # 查找榜单项
                item_elements = container.select('div[class^="cc-cd-cb"] a, div.cc-cd-cb a')
                
                for idx, elem in enumerate(item_elements, 1):
                    try:
                        # 提取标题
                        title = elem.get_text(strip=True)
                        if not title:
                            continue
                        
                        # 提取链接
                        url = elem.get('href', '')
                        if url and not url.startswith('http'):
                            url = 'https://tophub.today' + url
                        
                        # 提取热度值(从相邻元素或title属性)
                        heat = None
                        heat_elem = elem.select_one('.heat, [class*="heat"], .hot, [class*="hot"]')
                        if heat_elem:
                            heat = self._parse_heat_value(heat_elem.get_text())
                        
                        # 创建数据对象
                        item = HotItem(
                            platform=platform,
                            ranking=idx,
                            title=title,
                            url=url,
                            heat=heat,
                            timestamp=datetime.now().isoformat()
                        )
                        items.append(item)
                        
                    except Exception as e:
                        logger.warning(f"解析榜单项时出错: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"解析平台容器时出错: {e}")
                continue
        
        logger.info(f"成功解析 {len(items)} 条热榜数据")
        return items
    
    def scrape(self) -> List[HotItem]:
        """执行爬取任务"""
        logger.info("开始爬取今日热榜...")
        
        # 获取页面
        html = self._make_request(self.BASE_URL)
        if not html:
            logger.error("获取页面失败")
            return []
        
        # 解析数据
        items = self.parse_page(html)
        
        logger.info(f"爬取完成，共获取 {len(items)} 条数据")
        return items
    
    def save_to_json(self, items: List[HotItem], filepath: str):
        """保存数据到JSON文件"""
        data = [item.to_dict() for item in items]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"数据已保存到: {filepath}")
    
    def save_to_csv(self, items: List[HotItem], filepath: str):
        """保存数据到CSV文件"""
        import csv
        
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


# 使用示例
if __name__ == "__main__":
    # 配置代理池(可选)
    proxy_pool = [
        # "http://user:pass@host:port",
        # "http://host:port",
    ]
    
    # 创建爬虫实例
    scraper = TopHubScraper(
        delay_range=(2, 3),      # 2-3秒请求间隔
        max_retries=3,            # 最大重试3次
        proxy_pool=proxy_pool,    # 代理池
        timeout=30                # 30秒超时
    )
    
    # 执行爬取
    items = scraper.scrape()
    
    # 保存数据到桌面
    if items:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        json_file = os.path.join(desktop_path, f"tophub_{timestamp}.json")
        csv_file = os.path.join(desktop_path, f"tophub_{timestamp}.csv")
        
        scraper.save_to_json(items, json_file)
        scraper.save_to_csv(items, csv_file)
        
        # 打印前10条数据预览
        print("\n=== 数据预览 (前10条) ===")
        for item in items[:10]:
            print(f"[{item.platform}] #{item.ranking} {item.title[:50]}... (热度: {item.heat})")
    else:
        print("未获取到数据")