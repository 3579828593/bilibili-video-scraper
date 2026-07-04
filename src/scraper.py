# -*- coding: utf-8 -*-
"""
视频抓取模块 - 批量获取 UP 主全部视频数据

功能：
- 通过 WBI 签名的 Bilibili API 分页抓取视频列表
- 自动处理分页、重试和错误恢复
- 支持进度显示和数据持久化（JSON）
"""

import json
import time
import sys
import os
from typing import Optional

import requests

from .wbi_signer import generate_signed_params, SEARCH_API_URL


class BilibiliScraper:
    """B站视频标题抓取器"""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://space.bilibili.com/",
        "Accept": "application/json",
    }

    def __init__(
        self,
        mid: int,
        output_path: Optional[str] = None,
        page_size: int = 50,
        max_retries: int = 3,
        delay: float = 0.5,
        verbose: bool = True,
    ):
        """
        初始化抓取器。

        Args:
            mid: UP 主 UID
            output_path: 输出 JSON 文件路径（默认自动生成）
            page_size: 每页数量（建议 50 或 100）
            max_retries: 单页最大重试次数
            delay: 请求间隔秒数（避免触发风控）
            verbose: 是否打印详细日志
        """
        self.mid = mid
        self.output_path = output_path or f"up_{mid}_videos.json"
        self.page_size = min(page_size, 100)  # B站限制最大 100
        self.max_retries = max_retries
        self.delay = delay
        self.verbose = verbose

        # 结果容器
        self.all_videos: list[dict] = []
        self.failed_pages: list[int] = []
        self.total_count: int = 0

    def _log(self, msg: str):
        """条件性日志输出"""
        if self.verbose:
            print(msg)

    def _fetch_page(self, page_num: int) -> Optional[dict]:
        """
        抓取单页数据。

        Args:
            page_num: 页码（从 1 开始）

        Returns:
            解析后的 JSON 数据字典，或 None（当所有重试都失败时）
        """
        params = generate_signed_params(self.mid, page_num, self.page_size)

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.get(
                    SEARCH_API_URL,
                    params=params,
                    headers=self.DEFAULT_HEADERS,
                    timeout=15,
                )
                data = resp.json()

                if data.get("code") == 0:
                    return data
                else:
                    error_msg = data.get("message", f"错误码 {data.get('code')}")
                    self._log(f"  ⚠️ 第 {page_num} 页第 {attempt} 次尝试: {error_msg}")

                    # 风控相关错误码，增加等待时间
                    if data.get("code") in (-352, -412, -799):
                        wait_time = self.delay * (attempt * 2)
                        self._log(f"  🔄 触发风控等待 {wait_time:.1f}s...")
                        time.sleep(wait_time)

            except requests.RequestException as e:
                self._log(f"  ❌ 第 {page_num} 页第 {attempt} 次网络异常: {e}")

            time.sleep(self.delay)

        return None

    def fetch_all(self) -> dict:
        """
        抓取指定 UP 主的全部视频数据。

        Returns:
            dict: 包含统计信息和视频列表的结果字典
        """
        self._log(f"🚀 开始抓取 UP 主 (UID: {self.mid}) 的全部视频...")
        self._log(f"   每页数量: {self.page_size} | 最大重试: {self.max_retries} | 间隔: {self.delay}s")
        print()

        # 第一页：获取总数
        self._log("📋 正在获取第一页（确定总数）...")
        first_page_data = self._fetch_page(1)

        if first_page_data is None:
            raise RuntimeError("❌ 无法获取第一页数据，请检查网络或 UID 是否正确")

        result_data = first_page_data["data"]["list"]["vlist"]
        self.total_count = first_page_data["data"]["page"]["count"]
        self.all_videos.extend(result_data)

        self._log(f"✅ 共发现 {self.total_count} 个视频")
        print()

        # 计算总页数
        total_pages = (self.total_count + self.page_size - 1) // self.page_size
        self._log(f"📄 总计 {total_pages} 页，开始分页抓取...")
        print()

        # 循环抓取剩余页面
        for page_num in range(2, total_pages + 1):
            self._log(
                f"⏳ [{page_num}/{total_pages}] "
                f"正在抓取... ({len(self.all_videos)}/{self.total_count})"
            )

            page_data = self._fetch_page(page_num)

            if page_data is not None:
                videos = page_data["data"]["list"]["vlist"]
                self.all_videos.extend(videos)
            else:
                self._log(f"  ❌ 第 {page_num} 页抓取失败，记录到失败列表")
                self.failed_pages.append(page_num)

            # 请求间隔
            time.sleep(self.delay)

        print()
        self._log("=" * 50)

        # 构建结果
        result = {
            "mid": self.mid,
            "fetched_count": len(self.all_videos),
            "total_count": self.total_count,
            "failed_pages": self.failed_pages,
            "videos": self.all_videos,
        }

        # 保存结果
        self._save_result(result)

        # 打印摘要
        success_rate = len(self.all_videos) / self.total_count * 100 if self.total_count > 0 else 0
        self._log(f"🎉 抓取完成！")
        self._log(f"   总数: {self.total_count} | 已获取: {len(self.all_videos)} | 成功率: {success_rate:.1f}%")
        if self.failed_pages:
            self._log(f"   失败页面: {self.failed_pages}")
        self._log(f"   数据已保存至: {self.output_path}")

        return result

    def _save_result(self, result: dict):
        """保存结果到 JSON 文件"""
        # 创建输出目录（如果需要）
        output_dir = os.path.dirname(self.output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)


# ============================================================
# 便捷函数
# ============================================================

def scrape_uploader(
    mid: int,
    output_path: Optional[str] = None,
    **kwargs,
) -> dict:
    """
    一键抓取 UP 主全部视频的便捷函数。

    Args:
        mid: UP 主 UID
        output_path: 输出文件路径
        **kwargs: 传递给 BilibiliScraper 的其他参数

    Returns:
        dict: 抓取结果
    """
    scraper = BilibiliScraper(mid=mid, output_path=output_path, **kwargs)
    return scraper.fetch_all()


if __name__ == "__main__":
    # 快速测试：抓取某幻的数据（前 5 条）
    print("=" * 50)
    print("  Bilibili Video Scraper - 测试模式")
    print("=" * 50)
    print()

    test_scraper = BilibiliScraper(
        mid=177230427,
        output_path="/tmp/test_output.json",
        verbose=True,
    )

    # 只测试第一页
    data = test_scraper._fetch_page(1)
    if data:
        videos = data["data"]["list"]["vlist"]
        total = data["data"]["page"]["count"]
        print(f"\n✅ 测试成功！共 {total} 个视频，首页返回 {len(videos)} 条")
        print(f"\n📝 前 3 条标题预览：")
        for i, v in enumerate(videos[:3], 1):
            print(f"   {i}. {v['title']}  (BV: {v['bvid']})")
    else:
        print("\n❌ 测试失败")
