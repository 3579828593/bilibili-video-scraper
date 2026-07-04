# -*- coding: utf-8 -*-
"""
数据分析模块 - 视频标题智能分析与统计

功能：
- 从标题中提取游戏名（基于正则 + 常见游戏库匹配）
- 统计各游戏出现频次
- 按类型分类（FPS、恐怖、独立、RPG 等）
- 生成 Markdown 格式分析报告
"""

import json
import re
import os
from collections import Counter, defaultdict
from datetime import datetime
from typing import Optional

# ============================================================
# 常见游戏名称库（用于模糊匹配）
# ============================================================

GAME_LIBRARY = {
    # FPS / 战术射击
    "PUBG": ["绝地求生", "PUBG", "吃鸡", "大逃杀"],
    "无畏契约": ["无畏契约", "VALORANT", "Valorant", "瓦罗兰特", "瓦"],
    "CS2": ["CS2", "CS:GO", "反恐精英", "csgo"],
    "APEX": ["APEX", "Apex英雄", "apex"],
    "Super People": ["超级人类", "Super People", "superpeople", "SP"],
    "彩虹六号": ["彩虹六号", "R6", "r6s", "围攻"],
    "守望先锋": ["守望先锋", "OW", "overwatch"],
    "使命召唤": ["使命召唤", "COD", "Call of Duty"],
    "战地": ["战地", "Battlefield"],
    "泰坦陨落": ["泰坦陨落", "Titanfall"],

    # 恐怖 / 惊悚
    "生化危机": ["生化危机", "Resident Evil", "RE", "生化危机4", "RE4"],
    "恐惧饥荒": ["恐惧饥荒", "Dread Hunger"],
    "德州电锯杀人狂": ["德州电锯杀人狂", "Texas Chain Saw Massacre"],
    "黎明杀机": ["黎明杀机", "Dead by Daylight", "DBD"],
    "纸嫁衣": ["纸嫁衣"],
    "港诡实录": ["港诡实录"],
    "女鬼桥": ["女鬼桥"],
    "逃生": ["逃生", "Outlast"],
    "小小梦魇": ["小小梦魇", "Little Nightmares"],
    "后室": ["后室", "The Backrooms"],
    "怪奇物语": ["怪奇物语"],

    # 独立 / 趣味
    "糖豆人": ["糖豆人", "Fall Guys", "糖豆"],
    "鹅鸭杀": ["鹅鸭杀", "Goose Goose Duck", "鹅鸭"],
    "太空狼人杀": ["太空狼人杀", "Among Us", "among us"],
    "猛兽派对": ["猛兽派对", "动物派对", "Party Animals"],
    "人类一败涂地": ["人类一败涂地", "HUMANKIND", "人类"],
    "只狼": ["只狼", "Sekiro", "只狼：影逝二度"],
    "艾尔登法环": ["艾尔登法环", "Elden Ring", "ELDEN RING", "老头环"],
    "赛博朋克2077": ["赛博朋克", "Cyberpunk 2077", "Cyberpunk", "赛博朋克2077"],
    "匹诺曹的谎言": ["匹诺曹的谎言", "Lies of P", "匹诺曹"],
    "幻兽帕鲁": ["幻兽帕鲁", "Palworld", "帕鲁"],
    "潜水员戴夫": ["潜水员戴夫", "Dave the Diver", "戴夫"],
    "植物大战僵尸": ["植物大战僵尸", "PVZ", "pvz", "随机版"],
    "斗蛐蛐": ["斗蛐蛐"],
    "弹丸论破": ["弹丸论破", "Danganronpa"],
    "黑色幽默": ["黑色幽默"],
    "火山的女儿": ["火山的女儿"],
    "星露谷物语": ["星露谷物语", "Stardew Valley"],
    "以撒的结合": ["以撒", "Isaac", "以撒的结合"],
    "杀戮尖塔": ["杀戮尖塔", "Slay the Spire"],
    "吸血鬼幸存者": ["吸血鬼幸存者", "Vampire Survivors"],
    "土豆兄弟": ["土豆兄弟", "Brotato"],

    # RPG / 开放世界
    "博德之门3": ["博德之门", "Baldur's Gate 3", "BG3", "博德3"],
    "塞尔达传说": ["塞尔达", "Zelda", "旷野之息", "王国之泪"],
    "原神": ["原神", "Genshin"],
    "崩坏：星穹铁道": ["崩铁", "星穹铁道", "Honkai Star Rail"],
    "最终幻想": ["最终幻想", "Final Fantasy", "FF"],
    "巫师3": ["巫师", "Witcher"],
    "荒野大镖客": ["荒野大镖客", "RDR", "Red Dead"],

    # 其他常见
    "我的世界": ["我的世界", "Minecraft", "MC", "minecraft"],
    "Roblox": ["roblox", "Roblox"],
    "VRChat": ["VRChat", "vrchat"],
    "模拟山羊": ["模拟山羊"],
    "模拟人生": ["模拟人生", "Sims"],
    " GTA ": ["GTA", "侠盗猎车手"],
    "荒野乱斗": ["荒野乱斗", "Brawl Stars"],
    "英雄联盟": ["英雄联盟", "LOL", "lol"],
    "王者荣耀": ["王者荣耀", "王者"],
    "永劫无间": ["永劫无间", "Naraka"],
    "燕云十六声": ["燕云十六声"],
    "明末：渊虚之羽": ["明末", "渊虚之羽"],
    "逃离塔科夫": ["逃离塔科夫", "塔科夫", "Tarkov"],
}


def extract_game_from_title(title: str) -> list[str]:
    """
    从视频标题中提取可能的游戏名称。

    Args:
        title: 视频标题文本

    Returns:
        匹配到的游戏名列表（可能有多个）
    """
    found_games = []
    title_lower = title.lower()

    for game_name, aliases in GAME_LIBRARY.items():
        for alias in aliases:
            if alias.lower() in title_lower:
                if game_name not in found_games:
                    found_games.append(game_name)
                break  # 一个游戏只需命中一个别名即可

    return found_games


def categorize_game(game_name: str) -> str:
    """
    将游戏归类到更广泛的类别。

    Args:
        game_name: 游戏名称

    Returns:
        类别字符串
    """
    fps_tactical = {"PUBG", "无畏契约", "CS2", "APEX", "Super People",
                     "彩虹六号", "守望先锋", "使命召唤", "战地", "泰坦陨落",
                     "逃离塔科夫", "永劫无间"}
    horror = {"生化危机", "恐惧饥荒", "德州电锯杀人狂", "黎明杀机",
              "纸嫁衣", "港诡实录", "女鬼桥", "逃生", "小小梦魇", "后室", "怪奇物语"}
    fps_shooter = {"VRChat"}  # VRChat 常带射击元素
    casual_party = {"糖豆人", "鹅鸭杀", "太空狼人杀", "猛兽派对", "人类一败涂地"}
    action_rpg = {"只狼", "艾尔登法环", "赛博朋克2077", "匹诺曹的谎言",
                  "博德之门3", "最终幻想", "巫师3", "荒野大镖客",
                  "明末：渊虚之羽", "原神", "崩坏：星穹铁道", "燕云十六声"}
    indie_fun = {"植物大战僵尸", "斗蛐蛐", "弹丸论破", "黑色幽默",
                 "火山的女儿", "星露谷物语", "以撒的结合", "杀戮尖塔",
                 "吸血鬼幸存者", "土豆兄弟", "潜水员戴夫", "幻兽帕鲁"}
    sandbox = {"我的世界", "Roblox", "GTA ", "模拟山羊", "模拟人生"}
    moba = {"英雄联盟", "王者荣耀", "荒野乱斗"}

    if game_name in fps_tactical:
        return "FPS / 战术射击"
    elif game_name in horror:
        return "恐怖 / 惊悚"
    elif game_name in fps_shooter:
        return "FPS / 射击"
    elif game_name in casual_party:
        return "休闲 / 派对"
    elif game_name in action_rpg:
        return "动作 / RPG"
    elif game_name in indie_fun:
        return "独立 / 趣味"
    elif game_name in sandbox:
        return "沙盒 / 开放世界"
    elif game_name in moba:
        return "MOBA"
    else:
        return "其他"


class VideoAnalyzer:
    """视频数据分析器"""

    def __init__(self, data_source: str | dict):
        """
        初始化分析器。

        Args:
            data_source: JSON 文件路径或已加载的数据字典
        """
        if isinstance(data_source, str):
            with open(data_source, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = data_source

        self.videos = self.data.get("videos", [])
        self.mid = self.data.get("mid", "unknown")

    def analyze(self) -> dict:
        """
        执行完整分析，返回结构化结果。

        Returns:
            包含各项统计数据的字典
        """
        total = len(self.videos)
        print(f"📊 开始分析 {total} 条视频数据...")

        # 提取每条视频的游戏标签
        game_list = []
        category_counter = Counter()
        yearly_counts = defaultdict(int)
        monthly_top_plays = []

        for video in self.videos:
            title = video.get("title", "")
            games = extract_game_from_title(title)
            game_list.extend(games)

            for g in games:
                cat = categorize_game(g)
                category_counter[cat] += 1

            # 年份统计
            pub_date = video.get("created", 0)
            if pub_date:
                year = datetime.fromtimestamp(pub_date).strftime("%Y")
                yearly_counts[year] += 1

            # 收集播放量用于排行
            play_count = int(video.get("play", 0))
            monthly_top_plays.append({
                "title": title,
                "play": play_count,
                "bvid": video.get("bvid", ""),
            })

        # 游戏频次排名
        game_counter = Counter(game_list)
        top_games = game_counter.most_common(30)

        # 类型分布
        category_dist = dict(category_counter.most_common())

        # 播放量 Top 10
        top_plays = sorted(monthly_top_plays, key=lambda x: x["play"], reverse=True)[:10]

        result = {
            "mid": self.mid,
            "total_videos": total,
            "unique_games": len(game_counter),
            "top_games": top_games,
            "category_distribution": category_dist,
            "yearly_distribution": dict(sorted(yearly_counts.items())),
            "top_10_by_plays": top_plays,
        }

        return result

    def generate_report(
        self,
        output_path: Optional[str] = None,
        include_all_titles: bool = True,
    ) -> str:
        """
        生成 Markdown 格式的分析报告。

        Args:
            output_path: 输出文件路径（为 None 则不保存文件）
            include_all_titles: 是否在报告中包含全部标题列表

        Returns:
            Markdown 报告文本
        """
        analysis = self.analyze()

        lines = []
        lines.append("# B站 UP 主视频数据分析报告\n")
        lines.append(f"> **UP 主 UID**: {analysis['mid']}")
        lines.append(f"> **视频总数**: {analysis['total_videos']}")
        lines.append(f"> **涉及游戏**: {analysis['unique_games']} 个不同游戏")
        lines.append(f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # ---- Top 游戏 ----
        lines.append("## 🎮 Top 30 游戏（按出现次数）\n")
        lines.append("| 排名 | 游戏 | 出现次数 | 占比 |")
        lines.append("|------|------|----------|------|")
        total = analysis["total_videos"]
        for i, (game, count) in enumerate(analysis["top_games"], 1):
            pct = count / total * 100
            lines.append(f"| {i} | {game} | {count} | {pct:.1f}% |")
        lines.append("")

        # ---- 类型分布 ----
        lines.append("## 📂 游戏类型分布\n")
        lines.append("| 类型 | 数量 | 占比 |")
        lines.append("|------|------|------|")
        for cat, count in analysis["category_distribution"].items():
            pct = count / total * 100
            lines.append(f"| {cat} | {count} | {pct:.1f}% |")
        lines.append("")

        # ---- 年度趋势 ----
        lines.append("## 📅 年度发布数量趋势\n")
        lines.append("| 年份 | 视频数 |")
        lines.append("|------|--------|")
        for year, count in analysis["yearly_distribution"].items():
            lines.append(f"| {year} | {count} |")
        lines.append("")

        # ---- 播放 Top 10 ----
        lines.append("## 🔥 播放量 Top 10 视频\n")
        lines.append("| 排名 | 标题 | 播放量 | BV号 |")
        lines.append("|------|------|--------|------|")
        for i, v in enumerate(analysis["top_10_by_plays"], 1):
            play_str = f"{v['play']:,}"
            short_title = v["title"][:50] + ("..." if len(v["title"]) > 50 else "")
            lines.append(f"| {i} | {short_title} | {play_str} | {v['bvid']} |")
        lines.append("")

        # ---- 全部标题列表 ----
        if include_all_titles:
            lines.append("---\n")
            lines.append("## 📋 全部视频标题列表\n")
            for i, video in enumerate(self.videos, 1):
                title = video.get("title", "")
                bvid = video.get("bvid", "")
                date_str = ""
                created = video.get("created", 0)
                if created:
                    date_str = datetime.fromtimestamp(created).strftime("%Y-%m-%d")
                lines.append(f"{i}. **{title}** `{bvid}` ({date_str})")
            lines.append("")

        report_text = "\n".join(lines)

        # 保存文件
        if output_path:
            out_dir = os.path.dirname(output_path)
            if out_dir and not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            print(f"✅ 分析报告已保存至: {output_path}")

        return report_text


if __name__ == "__main__":
    # 测试模式
    import sys
    test_file = sys.argv[1] if len(sys.argv) > 1 else None
    if test_file and os.path.exists(test_file):
        analyzer = VideoAnalyzer(test_file)
        report = analyzer.generate_report(output_path="/tmp/test_analysis.md")
        print("\n" + "=" * 40)
        print("报告预览（前 500 字符）：")
        print("=" * 40)
        print(report[:500])
    else:
        print("用法: python -m src.analyzer <json_file>")
