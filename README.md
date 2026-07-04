# 🎬 Bilibili Video Scraper

> **B站 UP 主视频标题批量抓取与分析工具** — 基于 WBI 签名的 Bilibili API，一键获取任意 UP 主的全部视频元数据，并自动生成智能分析报告。

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ 功能特性

- 🚀 **全量抓取** — 通过 WBI 签名 API 自动分页获取 UP 主全部视频（支持数百甚至数千条）
- 🔐 **无需登录** — 基于 WBI (Web Bilibili Interface) 签名算法，无需 Cookie 即可调用
- 📊 **智能分析** — 自动从标题提取游戏名称、分类统计、年度趋势、播放量排行
- 📝 **Markdown 报告** — 一键生成结构化的 Markdown 分析报告
- ⚡ **断点续传** — 失败页面记录在案，支持后续补抓
- 🛠️ **CLI 工具** — 命令行参数灵活配置，支持自定义输出路径、分页大小、重试策略
- 📦 **即开即用** — 零配置，`pip install -r requirements.txt && python main.py --mid <UID>` 即可运行

---

## 📸 效果预览

### 抓取过程
```
=======================================================
   🎬  Bilibili Video Scraper  v1.0.0
   B站UP主视频标题批量抓取与分析工具
=======================================================

🚀 开始抓取 UP 主 (UID: 177230427) 的全部视频...
   每页数量: 50 | 最大重试: 3 | 间隔: 0.5s

📋 正在获取第一页（确定总数）...
✅ 共发现 804 个视频

📄 总计 17 页，开始分页抓取...

⏳ [2/17] 正在抓取... (50/804)
⏳ [3/17] 正在抓取... (100/804)
...

🎉 抓取完成！
   总数: 804 | 已获取: 804 | 成功率: 100.0%
   数据已保存至: up_177230427_videos.json
```

### 分析报告示例
```
# B站 UP 主视频数据分析报告

> **UP 主 UID**: 177230427
> **视频总数**: 804
> **涉及游戏**: 348 个不同游戏

## 🎮 Top 30 游戏（按出现次数）

| 排名 | 游戏 | 出现次数 | 占比 |
|------|------|----------|------|
| 1    | PUBG | 276      | 34.3%|
| 2    | Super People | 34 | 4.2% |
| ...

## 📂 游戏类型分布

| 类型         | 数量 | 占比 |
|--------------|------|------|
| FPS / 战术射击 | 290 | 36.1% |
| 恐怖 / 惊悚   | 143 | 17.8% |
| ...
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- 网络连接（需能访问 B 站 API）

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/bilibili-video-scraper.git
cd bilibili-video-scraper

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
```

### 使用方法

#### 基础用法 — 仅抓取数据

```bash
# 抓取某幻君的全部视频
python main.py --mid 177230427

# 自定义输出文件名
python main.py --mid 177230427 -o my_uploader.json

# 加大每页数量以加快速度
python main.py --mid 177230427 --page-size 100
```

#### 高级用法 — 抓取 + 自动分析

```bash
# 抓取后自动生成完整分析报告
python main.py --mid 177230427 --analyze

# 指定报告输出路径
python main.py --mid 177230427 --analyze --report report.md
```

#### 离线分析 — 使用已有数据

```bash
# 对已下载的 JSON 数据进行分析（不重新抓取）
python main.py -i up_177230427_videos.json --analyze
```

#### 调优参数

```bash
# 风控严重时增加请求间隔和重试次数
python main.py --mid 177230427 --delay 1.5 --retries 5

# 静默模式（减少日志输出）
python main.py --mid 177230427 -q
```

### 完整参数列表

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--mid` | — | *(必填)* | 目标 UP 主的 UID（数字 ID） |
| `--input` | `-i` | — | 已有 JSON 数据文件路径（与 --mid 二选一） |
| `--output` | `-o` | `up_{mid}.json` | 输出 JSON 文件路径 |
| `--analyze` | — | `False` | 是否在抓取后自动生成分析报告 |
| `--report` | — | `up_{mid}.md` | 分析报告输出路径 |
| `--page-size` | — | `50` | 每页抓取数量（1~100） |
| `--delay` | — | `0.5` | 请求间隔秒数 |
| `--retries` | — | `3` | 单页最大重试次数 |
| `--quiet` | `-q` | `False` | 静默模式 |

---

## 📁 项目结构

```
bilibili-video-scraper/
├── src/                      # 核心源码包
│   ├── __init__.py          # 包初始化 & 版本信息
│   ├── wbi_signer.py        # WBI 签名模块（核心算法）
│   ├── scraper.py           # 视频抓取模块（分页、重试、持久化）
│   └── analyzer.py          # 数据分析模块（游戏提取、统计、报告生成）
├── examples/                 # 示例文件
│   └── README.md            # 示例说明
├── tests/                    # 单元测试
│   └── test_scraper.py      # 测试用例
├── main.py                   # CLI 入口
├── requirements.txt          # Python 依赖
├── .gitignore               # Git 忽略规则
├── LICENSE                  # MIT 开源协议
└── README.md                # 本文件
```

---

## 🔧 核心模块说明

### 1. WBI 签名 (`src/wbi_signer.py`)

基于 [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) 实现的 WBI 签名算法：

```
请求流程：
  ① 调用 /x/web-interface/nav 获取 img_key + sub_key
  ② 对请求参数按 key 字典序排列，拼接为 query string
  ③ 将 img_key + sub_key 经混淆表 (MIXIN_KEY_ENC_TABS) 重排 → 取前 32 位 = mixin_key
  ④ 计算 MD5(query + mixin_key) → 得到 w_rid
  ⑤ 将 w_rid 和 wts(时间戳) 附加到原始参数中
  ⑥ 发起带签名的 API 请求
```

### 2. 视频抓取 (`src/scraper.py`)

- `BilibiliScraper` 类：封装完整的抓取逻辑
- 自动分页：根据第一页返回的 `page.count` 计算总页数
- 智能重试：针对风控错误码 (-352/-412/-799) 自动延长等待时间
- JSON 输出：包含完整元数据（标题、BV号、发布时间、播放量、简介等）

### 3. 数据分析 (`src/analyzer.py`)

- **游戏识别**：内置 60+ 游戏别名库，支持模糊匹配
- **类型分类**：FPS / 恐怖 / RPG / 独立 / 沙盒 / MOBA 等 9 大类
- **统计维度**：Top 游戏、类型分布、年度趋势、播放量排行
- **报告输出**：结构化 Markdown，支持全部标题列表附录

---

## 📊 输出数据格式

### JSON 结构 (`up_{mid}_videos.json`)

```json
{
  "mid": 177230427,
  "fetched_count": 804,
  "total_count": 804,
  "failed_pages": [],
  "videos": [
    {
      "title": "【某幻君2024.02.21】xxx【游戏名】",
      "bvid": "BV1xxxxxxxx",
      "created": 1708502400,
      "play": 1234567,
      "length": "12:34",
      "description": "...",
      "comment": 1234
    }
  ]
}
```

### 分析报告字段

- Top 30 游戏（出现次数 + 占比）
- 9 大类型分布统计
- 年度发布数量趋势图（表格形式）
- 播放量 Top 10 视频
- 全部视频标题列表（含 BV 号和发布日期）

---

## ⚠️ 注意事项

1. **频率限制**：B 站对 API 有频率限制，默认 0.5s 间隔。若触发风控（错误码 -352），可使用 `--delay 1.5` 增大间隔。
2. **WBI Key 更新**：签名密钥由 B 端动态下发，脚本每次运行时自动获取最新 key。
3. **数据完整性**：抓取结果中 `failed_pages` 字段会列出失败的页码，可据此手动补抓。
4. **仅限学习交流**：本工具仅供技术研究和个人学习使用，请遵守 B 站用户协议和 robots.txt 规则。

---

## 🤝 贡献指南

欢迎 Issue 和 Pull Request！

```bash
# Fork → 克隆 → 创建分支 → 提交 → PR
git checkout -b feature/amazing-feature
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature
```

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

- [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) — B站 API 文档 & WBI 签名算法参考
- [requests](https://docs.python-requests.org/) — HTTP 客户端库

---

## 📌 Star History

如果这个工具对你有帮助，欢迎给一个 ⭐ 支持一下！

<p align="center">
  <img src="https://api.star-history.com/svg?repos=YOUR_USERNAME/bilibili-video-scraper&type=Date" alt="Star History" />
</p>
