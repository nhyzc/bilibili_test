#!/usr/bin/env python3
"""Fetch and optionally download Bilibili video covers.

Usage examples:
  python bilibili_cover_fetcher.py --url "https://www.bilibili.com/video/BV1xx411c7mD"
  python bilibili_cover_fetcher.py --bvid "BV1xx411c7mD" --download ./cover.jpg
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


API_URL = "https://api.bilibili.com/x/web-interface/view"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.bilibili.com/",
}


class CoverFetcherError(RuntimeError):
    """Known user-facing errors for this tool."""


def extract_bvid(text: str) -> Optional[str]:
    """Extract BV id from arbitrary text (URL or plain id)."""
    match = re.search(r"(BV[0-9A-Za-z]{10})", text)
    return match.group(1) if match else None


def extract_aid(text: str) -> Optional[int]:
    """Extract av id from arbitrary text (URL or plain av123 / 123)."""
    av_match = re.search(r"(?:av|aid=)(\d+)", text, flags=re.IGNORECASE)
    if av_match:
        return int(av_match.group(1))
    if text.isdigit():
        return int(text)
    return None


def get_cover_url(*, bvid: str | None = None, aid: int | None = None, timeout: int = 10) -> str:
    """Fetch cover URL from Bilibili API."""
    if not bvid and not aid:
        raise CoverFetcherError("必须提供 bvid 或 aid 参数。")

    params = {}
    if bvid:
        params["bvid"] = bvid
    if aid:
        params["aid"] = aid

    try:
        import requests
    except ModuleNotFoundError as exc:
        raise CoverFetcherError("缺少 requests 依赖，请先安装 requirements.txt。") from exc

    try:
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise CoverFetcherError(f"网络请求失败: {exc}") from exc
    except ValueError as exc:
        raise CoverFetcherError("接口返回了非 JSON 数据。") from exc

    code = payload.get("code")
    if code != 0:
        msg = payload.get("message", "未知错误")
        raise CoverFetcherError(f"B 站接口返回错误 code={code}, message={msg}")

    data = payload.get("data") or {}
    cover = data.get("pic")
    if not cover:
        raise CoverFetcherError("未能从接口中解析到封面地址。")
    return cover


def download_cover(cover_url: str, output_path: Path, timeout: int = 20) -> Path:
    """Download cover image to local path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import requests
    except ModuleNotFoundError as exc:
        raise CoverFetcherError("缺少 requests 依赖，请先安装 requirements.txt。") from exc

    try:
        response = requests.get(cover_url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise CoverFetcherError(f"下载封面失败: {exc}") from exc

    output_path.write_bytes(response.content)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="爬取 B 站视频封面链接，并可选择下载到本地。")
    parser.add_argument("--url", help="视频链接，例如 https://www.bilibili.com/video/BVxxxx")
    parser.add_argument("--bvid", help="视频 bvid，例如 BV1xx411c7mD")
    parser.add_argument("--aid", type=int, help="视频 aid (av号数字部分)")
    parser.add_argument("--download", type=Path, help="下载封面图片到指定路径")
    parser.add_argument("--timeout", type=int, default=10, help="接口超时时间（秒）")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    bvid = args.bvid
    aid = args.aid

    if args.url:
        if not bvid:
            bvid = extract_bvid(args.url)
        if not aid:
            aid = extract_aid(args.url)

    if not bvid and not aid:
        print("错误：请提供 --url、--bvid 或 --aid。", file=sys.stderr)
        return 2

    try:
        cover_url = get_cover_url(bvid=bvid, aid=aid, timeout=args.timeout)
        print(f"封面链接: {cover_url}")

        if args.download:
            file_path = download_cover(cover_url, args.download)
            print(f"已下载到: {file_path}")
    except CoverFetcherError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
