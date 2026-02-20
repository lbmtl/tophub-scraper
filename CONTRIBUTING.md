# 贡献指南

感谢您对 TopHub Scraper 项目的关注！我们欢迎各种形式的贡献。

## 🐛 提交 Issue

在提交 Issue 前，请：

1. 搜索现有 Issue，避免重复提交
2. 使用清晰的标题描述问题
3. 提供以下信息：
   - Python 版本 (`python --version`)
   - 操作系统
   - 复现步骤
   - 错误日志（如有）

## 🔧 提交 Pull Request

### 开发流程

1. **Fork 仓库**
   ```bash
   git clone https://github.com/yourusername/tophub-scraper.git
   cd tophub-scraper
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **安装开发依赖**
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8
   ```

4. **代码规范**
   - 使用 Black 格式化代码：`black .`
   - 遵循 PEP 8 规范
   - 添加必要的注释和文档字符串

5. **测试**
   ```bash
   pytest tests/
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/your-feature-name
   ```

7. **创建 PR**
   - 提供清晰的 PR 描述
   - 关联相关 Issue
   - 确保 CI 检查通过

### Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

示例：
```
feat: add proxy rotation support
fix: handle timeout exception in edge scraper
docs: update README with API examples
```

## 📝 代码风格

- 使用 4 空格缩进
- 行长度限制 100 字符
- 函数和类添加文档字符串
- 类型注解（可选但推荐）

## 🧪 测试

- 为新功能添加测试用例
- 确保测试覆盖率不降低
- 测试应独立运行，不依赖外部网络

## 📄 许可证

通过提交 PR，您同意您的贡献将采用 MIT 许可证。

## 💬 联系我们

如有问题，欢迎：
- 在 Issue 中讨论
- 发送邮件至 [your-email@example.com]

感谢您的贡献！
