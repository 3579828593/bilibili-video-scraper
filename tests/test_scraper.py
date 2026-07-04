# -*- coding: utf-8 -*-
"""
单元测试 - Bilibili Video Scraper

测试覆盖：
- WBI 签名算法正确性
- 游戏名称提取准确性
- 类型分类映射完整性
- JSON 数据解析能力

运行方式：
    python -m pytest tests/test_scraper.py -v
    # 或
    python tests/test_scraper.py
"""

import sys
import os
import json
import unittest

# 确保可以导入 src 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.wbi_signer import (
    _get_mixin_key,
    calc_wbi_sign,
    MIXIN_KEY_ENC_TABS,
)
from src.analyzer import (
    extract_game_from_title,
    categorize_game,
    GAME_LIBRARY,
)


class TestMixinKey(unittest.TestCase):
    """测试混淆表算法"""

    def test_mixin_key_length(self):
        """mixin_key 应该恰好 32 位"""
        orig = "a" * 64  # 模拟 img_key + sub_key
        result = _get_mixin_key(orig)
        self.assertEqual(len(result), 32)

    def test_mixin_key_deterministic(self):
        """相同输入应产生相同输出"""
        orig = "test1234abcxyz9876" * 4  # 72 chars, > 64 满足索引需求
        r1 = _get_mixin_key(orig)
        r2 = _get_mixin_key(orig)
        self.assertEqual(r1, r2)

    def test_mixin_key_uses_enc_tabs(self):
        """应使用 MIXIN_KEY_ENC_TABS 进行索引"""
        # 构造已知输入
        orig = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%"
        result = _get_mixin_key(orig)
        # 验证每个字符都来自原字符串（只是顺序被打乱）
        for ch in result:
            self.assertIn(ch, orig)


class TestWBISign(unittest.TestCase):
    """测试 WBI 签名"""

    def test_calc_wbi_sign_adds_fields(self):
        """calc_wbi_sign 应添加 w_rid 和 wts"""
        params = {"mid": "177230427", "ps": "50", "pn": "1"}
        signed = calc_wbi_sign(
            params,
            img_key="test_img_key_for_unit_test_padding_32",
            sub_key="test_sub_key_for_unit_test_padding_32",
        )
        self.assertIn("w_rid", signed)
        self.assertIn("wts", signed)
        self.assertEqual(len(signed["w_rid"]), 32)  # MD5 hex digest

    def test_calc_wbi_sign_preserves_original_params(self):
        """签名不应删除或修改原有参数"""
        params = {"mid": "123", "ps": "100", "order": "pubdate"}
        original_keys = set(params.keys())
        signed = calc_wbi_sign(
            params,
            img_key="a" * 32,
            sub_key="b" * 32,
        )
        self.assertTrue(original_keys.issubset(signed.keys()))

    def test_wts_is_recent_timestamp(self):
        """wts 应该是接近当前时间的时间戳"""
        import time
        params = {"mid": "123"}
        before = int(time.time())
        signed = calc_wbi_sign(params, img_key="x" * 32, sub_key="y" * 32)
        after = int(time.time()) + 2
        self.assertGreaterEqual(signed["wts"], before)
        self.assertLessEqual(signed["wts"], after)


class TestGameExtraction(unittest.TestCase):
    """测试游戏名称提取"""

    def test_pubg_extraction(self):
        titles = ["【PUBG】吃鸡日常", "绝地求生大逃杀", "今天吃鸡了"]
        for t in titles:
            games = extract_game_from_title(t)
            self.assertIn("PUBG", games, f"PUBG 未被识别: {t}")

    def test_valorant_extraction(self):
        titles = ["【无畏契约】排位", "瓦罗兰特日常", "Valorant 精彩操作"]
        for t in titles:
            games = extract_game_from_title(t)
            self.assertIn("无畏契约", games, f"无畏契约未被识别: {t}")

    def test_resident_evil_extraction(self):
        titles = ["生化危机4", "RE4 重制版", "Resident Evil"]
        for t in titles:
            games = extract_game_from_title(t)
            self.assertIn("生化危机", games, f"生化危机未被识别: {t}")

    def test_multi_game_in_one_title(self):
        """一条标题可能包含多个游戏"""
        title = "【无畏契约、PUBG、糖豆人】三合一"
        games = extract_game_from_title(title)
        self.assertIn("无畏契约", games)
        self.assertIn("PUBG", games)
        self.assertIn("糖豆人", games)

    def test_no_match_returns_empty(self):
        """无匹配时应返回空列表"""
        games = extract_game_from_title("今天天气真好")
        self.assertEqual(games, [])

    def test_case_insensitive(self):
        """匹配应对大小写不敏感"""
        games_low = extract_game_from_title("apex legends")
        games_up = extract_game_from_title("APEX LEGENDS")
        self.assertEqual(games_low, games_up)


class TestGameCategorization(unittest.TestCase):
    """测试游戏类型分类"""

    def test_fps_tactical_category(self):
        fps_games = ["PUBG", "无畏契约", "CS2", "APEX", "Super People", "彩虹六号"]
        for g in fps_games:
            cat = categorize_game(g)
            self.assertEqual(cat, "FPS / 战术射击", f"{g} 分类错误: {cat}")

    def test_horror_category(self):
        horror_games = ["生化危机", "恐惧饥荒", "纸嫁衣", "黎明杀机", "逃生"]
        for g in horror_games:
            cat = categorize_game(g)
            self.assertEqual(cat, "恐怖 / 惊悚", f"{g} 分类错误: {cat}")

    def test_indie_fun_category(self):
        indie_games = ["植物大战僵尸", "斗蛐蛐", "弹丸论破", "星露谷物语"]
        for g in indie_games:
            cat = categorize_game(g)
            self.assertEqual(cat, "独立 / 趣味", f"{g} 分类错误: {cat}")

    def test_unknown_game_fallback(self):
        """未知游戏应归类为'其他'"""
        cat = categorize_game("完全不存在的游戏名")
        self.assertEqual(cat, "其他")

    def test_all_library_games_categorized(self):
        """GAME_LIBRARY 中所有游戏都应有对应分类"""
        for game_name in GAME_LIBRARY:
            cat = categorize_game(game_name)
            self.assertNotEqual(cat, "未分类", f"{game_name} 无分类")


class TestDataParsing(unittest.TestCase):
    """测试 JSON 数据解析"""

    def setUp(self):
        """构造模拟数据"""
        self.sample_data = {
            "mid": 123456,
            "fetched_count": 3,
            "total_count": 3,
            "failed_pages": [],
            "videos": [
                {
                    "title": "【测试UP2024.01.01】PUBG 吃鸡【绝地求生】",
                    "bvid": "BV1TEST001",
                    "created": 1704067200,
                    "play": 100000,
                    "length": "10:00",
                    "description": "测试简介",
                    "comment": 500,
                },
                {
                    "title": "【测试UP2024.01.02】生化危机",
                    "bvid": "BV1TEST002",
                    "created": 1704153600,
                    "play": 200000,
                    "length": "20:30",
                    "description": "",
                    "comment": 300,
                },
                {
                    "title": "【测试UP】糖豆人",
                    "bvid": "BV1TEST003",
                    "created": 1704240000,
                    "play": 50000,
                    "length": "05:15",
                    "description": "趣味视频",
                    "comment": 100,
                },
            ],
        }
        # 写入临时文件供 Analyzer 使用
        self.temp_file = "/tmp/test_sample_data.json"
        with open(self.temp_file, "w", encoding="utf-8") as f:
            json.dump(self.sample_data, f, ensure_ascii=False)

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_analyzer_loads_data(self):
        from src.analyzer import VideoAnalyzer
        analyzer = VideoAnalyzer(self.sample_data)
        self.assertEqual(len(analyzer.videos), 3)
        self.assertEqual(analyzer.mid, 123456)

    def test_analyzer_extract_stats(self):
        from src.analyzer import VideoAnalyzer
        analyzer = VideoAnalyzer(self.sample_data)
        result = analyzer.analyze()
        self.assertEqual(result["total_videos"], 3)
        self.assertGreater(result["unique_games"], 0)
        self.assertIn("top_games", result)
        self.assertIn("category_distribution", result)

    def test_report_generation(self):
        from src.analyzer import VideoAnalyzer
        analyzer = VideoAnalyzer(self.sample_data)
        report = analyzer.generate_report(output_path="/tmp/test_report.md")
        self.assertIn("# B站 UP 主视频数据分析报告", report)
        self.assertIn("Top 30 游戏", report)
        self.assertIn("PUBG", report)
        self.assertTrue(os.path.exists("/tmp/test_report.md"))
        # 清理
        os.remove("/tmp/test_report.md")


if __name__ == "__main__":
    unittest.main(verbosity=2)
