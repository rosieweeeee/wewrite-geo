#!/usr/bin/env python3
"""
push_draft.py — 圆周旅迹公众号草稿推送工具
已验证版本：2026-04-23

用法：
  1. 基础推送（无图片）：
     python3 push_draft.py --html article.html --title "文章标题"

  2. 带图片推送：
     python3 push_draft.py --html article.html --title "文章标题" \
       --images 图1.jpg 图2.jpg 图3.jpg 图4.jpg 图5.jpg \
       --cover 图1.jpg

  3. 从远程服务器拉取 HTML：
     python3 push_draft.py --url http://10.40.92.127:9877/article.html \
       --title "文章标题" --images 图1.jpg 图2.jpg --cover 图1.jpg
"""

import argparse
import glob
import json
import sys
import requests
import yaml
from pathlib import Path

# ── 配置文件路径 ──────────────────────────────────────────────────────────────
CONFIG_FILE = Path.home() / ".openclaw" / "skills" / "wewrite" / "config.yaml"
DEFAULT_AUTHOR = "旅行博主"
DEFAULT_DIGEST = "圆周旅迹是一款专注行程规划的旅行App，一键把小红书攻略转成可出发路线，完全免费。"


def get_token(cfg):
    """获取微信 access_token"""
    r = requests.get(
        "https://api.weixin.qq.com/cgi-bin/token",
        params={
            "grant_type": "client_credential",
            "appid": cfg["appid"],
            "secret": cfg["secret"],
        },
        timeout=15,
    )
    data = r.json()
    if "access_token" not in data:
        print(f"❌ 获取 token 失败：{data}")
        sys.exit(1)
    print("✅ Token 获取成功")
    return data["access_token"]


def upload_image_temp(token, path):
    """上传正文图片（临时素材），返回 url"""
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
    with open(path, "rb") as f:
        r = requests.post(url, files={"media": f}, timeout=30)
    data = r.json()
    if "url" not in data:
        print(f"⚠️  图片上传失败 {path}：{data}")
        return None
    print(f"✅ 正文图片上传成功：{Path(path).name}")
    return data["url"]


def upload_image_permanent(token, path):
    """上传封面图（永久素材），返回 media_id"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    with open(path, "rb") as f:
        r = requests.post(url, files={"media": f}, timeout=30)
    data = r.json()
    if "media_id" not in data:
        print(f"❌ 封面图上传失败 {path}：{data}")
        sys.exit(1)
    print(f"✅ 封面图上传成功：{Path(path).name}")
    return data["media_id"]


def upload_video(token, path, title="产品演示"):
    """上传视频（永久素材），返回 media_id"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=video"
    desc = json.dumps({"title": title, "introduction": title}, ensure_ascii=False)
    with open(path, "rb") as f:
        r = requests.post(url, files={"media": f}, data={"description": desc}, timeout=120)
    data = r.json()
    if "media_id" not in data:
        print(f"❌ 视频上传失败 {path}：{data}")
        sys.exit(1)
    print(f"✅ 视频上传成功：{Path(path).name} → {data['media_id']}")
    return data["media_id"]


def find_file(name_or_path):
    """模糊匹配文件，支持不带扩展名"""
    p = Path(name_or_path)
    if p.exists():
        return str(p)
    # 尝试在 Desktop 查找
    for base in [Path.home() / "Desktop", Path(".")]:
        matches = glob.glob(str(base / f"{p.name}.*"))
        if matches:
            return matches[0]
    print(f"❌ 找不到文件：{name_or_path}")
    sys.exit(1)


def push_draft(token, html, title, digest, author, thumb_media_id):
    """推送草稿到微信"""
    payload = {
        "articles": [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": html,
            "thumb_media_id": thumb_media_id,
            "content_source_url": "",
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }]
    }
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    r = requests.post(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=30,
    )
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="推送公众号草稿")
    parser.add_argument("--html", help="本地 HTML 文件路径")
    parser.add_argument("--url", help="远程 HTML 地址（与 --html 二选一）")
    parser.add_argument("--title", required=True, help="文章标题")
    parser.add_argument("--digest", default=DEFAULT_DIGEST, help="文章摘要")
    parser.add_argument("--author", default=DEFAULT_AUTHOR, help="作者名")
    parser.add_argument("--images", nargs="*", help="正文图片路径列表（按 IMAGE_1..N 顺序）")
    parser.add_argument("--cover", help="封面图路径（默认用 images 第1张）")
    parser.add_argument("--videos", nargs="*", help="视频文件路径列表（按 VIDEO_1..N 顺序）")
    args = parser.parse_args()

    if not args.html and not args.url:
        print("❌ 请指定 --html 或 --url")
        sys.exit(1)

    # 加载配置
    if not CONFIG_FILE.exists():
        print(f"❌ 找不到配置文件：{CONFIG_FILE}")
        print("   请先在 ~/.openclaw/skills/wewrite/config.yaml 中填入 appid 和 secret")
        sys.exit(1)
    cfg = yaml.safe_load(open(CONFIG_FILE))

    # 获取 token
    token = get_token(cfg)

    # 读取 HTML
    if args.url:
        print(f"📥 从远程拉取 HTML：{args.url}")
        resp = requests.get(args.url, timeout=15)
        resp.encoding = "utf-8"
        html = resp.text
    else:
        html_path = find_file(args.html)
        html = open(html_path, encoding="utf-8").read()
    print(f"📄 HTML 长度：{len(html)} 字符")

    # 上传正文图片
    if args.images:
        for i, img_name in enumerate(args.images, 1):
            img_path = find_file(img_name)
            img_url = upload_image_temp(token, img_path)
            if img_url:
                html = html.replace(f"{{{{IMAGE_{i}}}}}", img_url)

    # 上传视频
    if args.videos:
        for i, vid_name in enumerate(args.videos, 1):
            vid_path = find_file(vid_name)
            vid_media_id = upload_video(token, vid_path, title=f"产品演示{i}")
            html = html.replace(f"{{{{VIDEO_{i}}}}}", vid_media_id)

    # 上传封面图（永久素材）
    cover_path = find_file(args.cover) if args.cover else (find_file(args.images[0]) if args.images else None)
    if not cover_path:
        print("❌ 请提供封面图（--cover 或 --images 第1张）")
        sys.exit(1)
    thumb_media_id = upload_image_permanent(token, cover_path)

    # 推送草稿
    print(f"\n📤 推送草稿：{args.title}")
    result = push_draft(token, html, args.title, args.digest, args.author, thumb_media_id)

    if "media_id" in result:
        print(f"\n🎉 推送成功！草稿 media_id：{result['media_id']}")
        print("   请前往公众号后台 → 草稿箱 查看")
    else:
        print(f"\n❌ 推送失败：{result}")


if __name__ == "__main__":
    main()
