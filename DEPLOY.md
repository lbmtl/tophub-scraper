# 今日热榜爬虫 - 服务部署指南

## 部署方式

### 方式 1: 交互式运行（推荐）

```bash
python tophub_service.py
```

选择菜单选项：
- **1**: 立即执行一次
- **2**: 每1小时自动执行
- **3**: 每2小时自动执行

### 方式 2: Windows 服务（后台运行）

#### 安装依赖
```bash
pip install pywin32 schedule
```

#### 安装服务
```bash
# 以管理员身份运行 PowerShell
python tophub_service.py install
python tophub_service.py start
```

#### 服务管理命令
```bash
python tophub_service.py start      # 启动服务
python tophub_service.py stop       # 停止服务
python tophub_service.py restart    # 重启服务
python tophub_service.py remove     # 卸载服务
```

#### 使用 Windows 服务管理器
```bash
# 打开服务管理器
services.msc

# 查找 "今日热榜爬虫服务"
# 可以设置开机自启、查看日志等
```

### 方式 3: 使用 NSSM（推荐用于生产环境）

NSSM (Non-Sucking Service Manager) 是更稳定的服务管理方案。

#### 下载 NSSM
https://nssm.cc/download

#### 安装服务
```bash
# 以管理员身份运行
nssm install TopHubScraper

# 在弹出的窗口中设置:
# Path: C:\Python313\python.exe
# Startup directory: C:\Users\s\.openclaw\workspace\scrapers
# Arguments: tophub_service.py
```

#### NSSM 管理命令
```bash
nssm start TopHubScraper      # 启动
nssm stop TopHubScraper       # 停止
nssm restart TopHubScraper    # 重启
nssm remove TopHubScraper     # 卸载
nssm status TopHubScraper     # 查看状态
```

### 方式 4: 计划任务（Windows Task Scheduler）

```powershell
# 创建每小时执行一次的计划任务
$Action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\s\.openclaw\workspace\scrapers\tophub_scraper.py" -WorkingDirectory "C:\Users\s\.openclaw\workspace\scrapers"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "TopHubScraper" -Action $Action -Trigger $Trigger -Settings $Settings -Description "今日热榜定时爬虫"
```

## 输出文件

服务运行后，数据将保存到：
- **桌面**: `C:\Users\s\Desktop\tophub_YYYYMMDD_HHMMSS.json`
- **桌面**: `C:\Users\s\Desktop\tophub_YYYYMMDD_HHMMSS.csv`
- **日志**: `C:\Users\s\Desktop\TopHubLogs\tophub_service.log`

## 配置文件

编辑 `tophub_service.py` 修改参数：

```python
self.scraper = TopHubScraper(
    delay_range=(2, 3),      # 请求间隔(秒)
    max_retries=3,            # 重试次数
    timeout=30                # 超时时间
)

# 定时频率
schedule.every(2).hours.do(self.crawl_job)  # 每2小时
```

## 监控与维护

### 查看日志
```bash
# 实时查看日志
tail -f "C:\Users\s\Desktop\TopHubLogs\tophub_service.log"

# 查看最后100行
Get-Content "C:\Users\s\Desktop\TopHubLogs\tophub_service.log" -Tail 100
```

### 数据清理
```powershell
# 删除7天前的旧数据
Get-ChildItem "C:\Users\s\Desktop\tophub_*" | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-7) } | Remove-Item
```

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| 服务无法启动 | 检查 Python 路径、依赖安装 |
| 爬取失败 | 查看日志文件，检查网络连接 |
| 数据为空 | 网站结构可能变更，需更新选择器 |
| 内存占用高 | 降低爬取频率，增加清理任务 |

## 安全建议

1. 定期更新 User-Agent
2. 使用住宅代理避免 IP 封禁
3. 控制爬取频率，避免对目标网站造成压力
4. 启用 Windows 防火墙规则

---

*部署时间: 2026-02-20*  
*维护者: 司空墨*