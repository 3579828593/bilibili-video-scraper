#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili Video Scraper - CLI 入口

一键抓取 B 站 UP 主的全部视频标题并生成分析报告。

用法示例：
    # 抓取某幻君的全部视频
    python main.py --mid 177230427

    # 抓取并生成分析报告
    python main.py --mid 177230427 --analyze

    # 自定义输出路径和每页数量
    python main.py --mid 177230427 -o my_data.json --page-size 100

    # 仅分析已有数据（不重新抓取）
    python main.py --input up_177230427_videos.json --analyze
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime

# 确保可以导入 src 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scraper import scrape_uploader, BilibiliScraper
from src.analyzer import VideoAnalyzer


def export_csv(json_path: str, csv_path: str | None = None) -> str:
    """将 JSON 数据导出为 CSV 格式

    Args:
        json_path: JSON 数据文件路径
        csv_path: CSV 输出路径（默认与 JSON 同目录，扩展名改为 .csv）

    Returns:
        实际保存的 CSV 文件路径
    """
    if csv_path is None:
        csv_path = json_path.rsplit(".", 1)[0] + ".csv"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    videos = data.get("videos", [])

    fieldnames = ["title", "bvid", "created", "created_date", "play", "length", "comment", "description"]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for v in videos:
            row = dict(v)
            # 将 Unix 时间戳转换为可读日期
            if "created" in row and row["created"]:
                try:
                    row["created_date"] = datetime.fromtimestamp(row["created"]).strftime("%Y-%m-%d %H:%M")
                except (ValueError, OSError):
                    row["created_date"] = ""
            writer.writerow(row)

    return csv_path


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="🎬 B站 UP 主视频标题批量抓取与分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --mid 177230427              # 抓取指定 UP 主
  %(prog)s --mid 177230427 --analyze     # 抓取 + 分析报告
  %(prog)s -i data.json --analyze        # 仅分析已有 JSON 数据
  %(prog)s --mid 123456 -o out.json      # 自定义输出路径
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--mid", type=int,
        help="目标 UP 主的 UID（数字 ID）",
    )
    group.add_argument(
        "--input", "-i", type=str,
        help="已有的 JSON 数据文件路径（跳过抓取，直接分析）",
    )

    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="输出 JSON 文件路径（默认: up_{mid}_videos.json）",
    )
    parser.add_argument(
        "--analyze", action="store_true",
        help="抓取完成后自动运行数据分析并生成报告",
    )
    parser.add_argument(
        "--report", type=str, default=None,
        help="分析报告输出路径（默认: up_{mid}_analysis.md）",
    )
    parser.add_argument(
        "--page-size", type=int, default=50,
        choices=range(1, 101), metavar="1-100",
        help="每页抓取数量（默认 50，最大 100）",
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="请求间隔秒数（默认 0.5，风控严重时可调高）",
    )
    parser.add_argument(
        "--retries", type=int, default=3,
        help="单页最大重试次数（默认 3）",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="静默模式，减少日志输出",
    )
    parser.add_argument(
        "--csv", action="store_true",
        help="同时导出 CSV 格式数据（方便用 Excel 打开）",
    )

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()

    print("=" * 55)
    print("   🎬  Bilibili Video Scraper  v1.0.0")
    print("   B站 UP 主视频标题批量抓取与分析工具")
    print("=" * 55)
    print()

    json_path = args.output
    result_data = None

    # ===== 阶段 1: 数据获取 =====
    if args.mid:
        # 通过 API 抓取
        if not json_path:
            json_path = f"up_{args.mid}_videos.json"

        try:
            result_data = scrape_uploader(
                mid=args.mid,
                output_path=json_path,
                page_size=args.page_size,
                max_retries=args.retries,
                delay=args.delay,
                verbose=not args.quiet,
            )
        except Exception as e:
            print(f"\n❌ 抓取失败: {e}")
            sys.exit(1)

    elif args.input:
        # 从已有文件读取
        json_path = args.input
        if not os.path.exists(json_path):
            print(f"❌ 文件不存在: {json_path}")
            sys.exit(1)
        print(f"📂 使用已有数据文件: {json_path}")

    # ===== 阶段 1.5: CSV 导出（可选）=====
    csv_path = None
    if args.csv:
        csv_path = export_csv(json_path)
        print(f"📄 CSV 已导出: {csv_path}")

    # ===== 阶段 2: 数据分析（可选）=====
    if args.analyze:
        print()
        print("=" * 55)
        print("   📊 数据分析阶段")
        print("=" * 55)
        print()

        report_path = args.report
        if not report_path and args.mid:
            report_path = f"up_{args.mid}_analysis.md"
        elif not report_path:
            report_path = "analysis_report.md"

        try:
            analyzer = VideoAnalyzer(json_path)
            report = analyzer.generate_report(
                output_path=report_path,
                include_all_titles=True,
            )
            print()
            print(f"🎉 全部完成！")
            print(f"   数据文件: {json_path}")
            if csv_path:
                print(f"   CSV 文件: {csv_path}")
            print(f"   分析报告: {report_path}")
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            sys.exit(1)

    else:
        print()
        print(f"✅ 数据已保存至: {json_path}")
        if csv_path:
            print(f"   CSV 文件: {csv_path}")
        print('   💡 使用 --analyze 参数可自动生成分析报告')


if __name__ == "__main__":
    main()
