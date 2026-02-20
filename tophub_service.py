#!/usr/bin/env python3
"""
今日热榜爬虫服务 - Windows 服务版
使用 pywin32 或 nssm 部署为 Windows 服务
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tophub_scraper import TopHubScraper

# 配置日志
log_dir = os.path.join(os.path.expanduser("~"), "Desktop", "TopHubLogs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "tophub_service.log"), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TopHubService:
    """爬虫服务类"""
    
    def __init__(self):
        self.scraper = TopHubScraper(
            delay_range=(2, 3),
            max_retries=3,
            timeout=30
        )
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.running = True
        
    def crawl_job(self):
        """定时爬取任务"""
        try:
            logger.info("开始定时爬取任务...")
            items = self.scraper.scrape()
            
            if items:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                json_file = os.path.join(self.desktop_path, f"tophub_{timestamp}.json")
                csv_file = os.path.join(self.desktop_path, f"tophub_{timestamp}.csv")
                
                self.scraper.save_to_json(items, json_file)
                self.scraper.save_to_csv(items, csv_file)
                
                logger.info(f"定时任务完成，保存了 {len(items)} 条数据")
            else:
                logger.warning("定时任务未获取到数据")
                
        except Exception as e:
            logger.error(f"定时任务出错: {e}", exc_info=True)
    
    def run_once(self):
        """运行一次"""
        logger.info("执行单次爬取...")
        self.crawl_job()
    
    def run_scheduler(self, interval_hours=1):
        """运行定时调度器"""
        logger.info(f"启动定时调度器，每 {interval_hours} 小时执行一次")
        
        # 设置定时任务
        schedule.every(interval_hours).hours.do(self.crawl_job)
        
        # 立即执行一次
        self.crawl_job()
        
        # 保持运行
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def stop(self):
        """停止服务"""
        logger.info("服务停止信号收到")
        self.running = False


def run_as_service():
    """作为 Windows 服务运行"""
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    
    class TopHubWindowsService(win32serviceutil.ServiceFramework):
        _svc_name_ = "TopHubScraperService"
        _svc_display_name_ = "今日热榜爬虫服务"
        _svc_description_ = "定时爬取今日热榜数据并保存到桌面"
        
        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)
            self.service = TopHubService()
            
        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.stop_event)
            self.service.stop()
            
        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            try:
                # 每2小时执行一次
                self.service.run_scheduler(interval_hours=2)
            except Exception as e:
                servicemanager.LogErrorMsg(str(e))
                
    win32serviceutil.HandleCommandLine(TopHubWindowsService)


def run_interactive():
    """交互式运行"""
    print("=" * 50)
    print("今日热榜爬虫服务")
    print("=" * 50)
    print("1. 立即执行一次")
    print("2. 每1小时自动执行")
    print("3. 每2小时自动执行")
    print("4. 退出")
    print("=" * 50)
    
    choice = input("请选择 (1-4): ").strip()
    
    service = TopHubService()
    
    if choice == "1":
        service.run_once()
    elif choice == "2":
        print("按 Ctrl+C 停止服务")
        try:
            service.run_scheduler(interval_hours=1)
        except KeyboardInterrupt:
            print("\n服务已停止")
    elif choice == "3":
        print("按 Ctrl+C 停止服务")
        try:
            service.run_scheduler(interval_hours=2)
        except KeyboardInterrupt:
            print("\n服务已停止")
    elif choice == "4":
        sys.exit(0)


if __name__ == "__main__":
    # 检查是否以服务方式运行
    if len(sys.argv) > 1 and sys.argv[1] in ['install', 'remove', 'start', 'stop', 'restart']:
        try:
            run_as_service()
        except ImportError:
            print("请先安装 pywin32: pip install pywin32")
            sys.exit(1)
    else:
        # 交互式运行
        run_interactive()