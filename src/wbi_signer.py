# -*- coding: utf-8 -*-
"""
WBI 签名模块 - Bilibili API 请求签名

基于 bilibili-API-collect (https://github.com/SocialSisterYi/bilibili-API-collect)
实现的 WBI (Web Bilibili Interface) 签名算法。

核心流程：
1. 获取 img_key 和 sub_key（从 B 站导航接口动态获取）
2. 对请求参数进行混淆表映射排序
3. 拼接 mixin_key 后计算 MD5 签名
"""

import hashlib
import json
import time
import random
import string
import requests

# 混淆表（固定值，来自 B 站前端源码）
MIXIN_KEY_ENC_TABS = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52
]

# API 端点
NAV_API_URL = "https://api.bilibili.com/x/web-interface/nav"
SEARCH_API_URL = "https://api.bilibili.com/x/space/wbi/arc/search"


def _get_mixin_key(orig: str) -> str:
    """根据混淆表对原始 key 进行重排，返回混淆后的 key（取前 32 位）"""
    return "".join([orig[i] for i in MIXIN_KEY_ENC_TABS])[:32]


def get_wbi_keys() -> tuple[str, str]:
    """
    从 B 站导航接口获取 WBI 签名所需的 img_key 和 sub_key。

    Returns:
        tuple: (img_key, sub_key)

    Raises:
        Exception: 当无法获取密钥时抛出异常
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.bilibili.com",
    }

    try:
        resp = requests.get(NAV_API_URL, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != 0:
            raise Exception(f"获取 WBI keys 失败: {data.get('message', '未知错误')}")

        wbi_img = data["data"]["wbi_img"]
        img_key = wbi_img["img_url"].split("/")[-1].split(".")[0]
        sub_key = wbi_img["sub_url"].split("/")[-1].split(".")[0]

        return img_key, sub_key

    except requests.RequestException as e:
        raise Exception(f"网络请求失败: {e}")


def calc_wbi_sign(params: dict, img_key: str, sub_key: str) -> dict:
    """
    计算请求参数的 WBI 签名。

    Args:
        params: 原始请求参数字典（不含 w_rid 和 wts）
        img_key: 图片密钥
        sub_key: 子密钥

    Returns:
        dict: 添加了 w_rid 和 wts 的完整参数字典
    """
    # 获取混淆后的 mixin_key
    orig = img_key + sub_key
    mixin_key = _get_mixin_key(orig)

    # 将当前时间戳添加到参数中
    params["wts"] = int(time.time())

    # 按 key 字典序排列后拼接为字符串
    sorted_params = {k: v for k, v in sorted(params.items())}
    query = "&".join([f"{k}={v}" for k, v in sorted_params.items()])

    # 拼接 mixin_key 后计算 MD5
    sign = hashlib.md5((query + mixin_key).encode()).hexdigest()

    # 返回带签名的完整参数
    params["w_rid"] = sign
    return params


def generate_signed_params(mid: int, page: int = 1, page_size: int = 50) -> dict:
    """
    为视频搜索接口生成完整的已签名参数。

    Args:
        mid: UP 主 UID
        page: 页码（从 1 开始）
        page_size: 每页数量（默认 50，最大 100）

    Returns:
        dict: 包含 w_rid 和 wts 的完整请求参数
    """
    img_key, sub_key = get_wbi_keys()

    params = {
        "mid": str(mid),
        "ps": str(page_size),
        "pn": str(page),
        "order": "pubdate",  # 按发布时间倒序
    }

    return calc_wbi_sign(params, img_key, sub_key)


# ============================================================
# 测试入口
# ============================================================
if __name__ == "__main__":
    print("测试 WBI 签名模块...")
    try:
        img_key, sub_key = get_wbi_keys()
        print(f"✅ 成功获取 WBI keys: img={img_key[:8]}..., sub={sub_key[:8]}...")

        test_params = {"mid": "177230427", "ps": "50", "pn": "1", "order": "pubdate"}
        signed = calc_wbi_sign(test_params, img_key, sub_key)
        print(f"✅ 签名成功: w_rid={signed['w_rid']}, wts={signed['wts']}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
