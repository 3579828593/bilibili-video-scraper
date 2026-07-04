# 示例文件

本目录包含使用示例和参考数据。

## 示例用法

### 示例 1：快速抓取 + 分析

```bash
cd bilibili-video-scraper

# 一条命令完成抓取和分析
python main.py --mid 177230427 --analyze --delay 0.8
```

生成的文件：
- `up_177230427_videos.json` — 全部 804 条视频的原始数据
- `up_177230427_analysis.md` — 完整的 Markdown 分析报告

### 示例 2：仅抓取数据（用于二次开发）

```bash
python main.py --mid 177230427 -o raw_data.json
```

然后在 Python 中导入使用：

```python
from src.scraper import BilibiliScraper
from src.analyzer import VideoAnalyzer

# 方式一：直接加载已有 JSON
analyzer = VideoAnalyzer("raw_data.json")
result = analyzer.analyze()
print(f"涉及 {result['unique_games']} 个不同游戏")

# 方式二：程序化调用抓取器
scraper = BilibiliScraper(mid=177230427, delay=1.0)
data = scraper.fetch_all()
print(f"共获取 {len(scraper.all_videos)} 条视频")
```

### 示例 3：自定义分析逻辑

```python
from src.analyzer import extract_game_from_title, categorize_game

titles = [
    "【某幻君2024.01.15】吃鸡日常【PUBG】",
    "【某幻君】生化危机4 重制版",
    "【某幻君2023.12.01】瓦罗兰特排位【无畏契约】",
]

for title in titles:
    games = extract_game_from_title(title)
    categories = [categorize_game(g) for g in games]
    print(f"标题: {title}")
    print(f"  → 游戏: {games} | 类型: {categories}")
```

### 示例 4：单独测试 WBI 签名

```bash
python -m src.wbi_signer
```

预期输出：
```
测试 WBI 签名模块...
✅ 成功获取 WBI keys: img=xxxxxx..., sub=xxxxxx...
✅ 签名成功: w_rid=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx, wts=xxxxxxxxxx
```

## 数据样例

以下为单条视频数据的字段说明（来自实际抓取）：

```json
{
  "comment": 1234,
  "typeid": 14,
  "play": 567890,
  "pic": "http://i0.hdslb.com/bfs/archive/xxx.jpg",
  "subtitle": "",
  "description": "视频简介内容...",
  "copyright": "",
  "title": "【某幻君2024.02.21】直播录像【无畏契约】",
  "long_title": "",
  "pubdate": 1708502400,
  "favorite": 5678,
  "mid": 177230427,
  "length": "12:34:56",
  "video_review": 0,
  "view": 567890,
  "bvid": "BV1xxxxxxxx",
  "created": 1708502400,
  "is_pay": 0,
  "is_union_video": 0,
  "is_steins_gate": 0
}
```

**关键字段速查表**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 视频标题（核心字段） |
| `bvid` | string | BV 号（唯一标识） |
| `created` | int | 发布时间戳（秒） |
| `play` / `view` | int | 播放量 |
| `comment` | int | 评论数 |
| `favorite` | int | 收藏数 |
| `length` | string | 时长（HH:MM:SS 格式） |
| `description` | string | 简介 |
| `pic` | string | 封面图 URL |
