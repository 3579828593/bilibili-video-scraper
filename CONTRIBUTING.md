# 贡献指南

感谢你对 Bilibili Video Scraper 项目的兴趣！欢迎通过以下方式参与贡献。

## 🐛 报告 Bug

1. 在 [Issues](https://github.com/3579828593/bilibili-video-scraper/issues) 页面搜索是否已有相同问题
2. 如果没有，使用 Bug Report 模板创建新 Issue
3. 请提供：操作系统、Python 版本、完整错误日志、复现步骤

## ✨ 提交新功能

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature-name`
3. 编写代码，确保通过测试：`python -m pytest tests/ -v`
4. 提交更改：`git commit -m 'feat: add your feature'`
5. 推送：`git push origin feature/your-feature-name`
6. 创建 Pull Request

## 📝 代码规范

- Python 3.8+ 兼容
- 遵循 PEP 8 风格
- 新功能需附带测试用例
- 函数和类需有 docstring
- Commit message 格式：`type: description`（type: feat/fix/docs/refactor/test/chore）

## 🧪 运行测试

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
python -m pytest tests/ -v --cov=src
```

## 📋 Pull Request 检查清单

- [ ] 代码通过所有测试
- [ ] 新功能有对应的测试用例
- [ ] 没有引入新的依赖（除非必要）
- [ ] 更新了相关文档
- [ ] Commit message 符合格式要求
