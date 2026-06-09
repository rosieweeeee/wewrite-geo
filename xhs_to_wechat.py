#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书笔记 -> 微信公众号草稿推送脚本
用法: python3 xhs_to_wechat.py notes_input.json
"""

import json, re, os, sys, time, requests

APPID  = "wxb32d492616da4383"
SECRET = "a6831decfa9886bb06ea5c22ef6eb9cd"

def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}"
    r = requests.get(url, timeout=10)
    r.encoding = "utf-8"
    data = r.json()
    if "access_token" not in data:
        raise Exception(f"获取token失败: {data}")
    print(f"✅ access_token OK")
    return data["access_token"]

def download_image(url, tag):
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        raise Exception(f"下载失败 {r.status_code}: {url}")
    ct = r.headers.get("Content-Type", "image/webp")
    ext = ".jpg" if "jpeg" in ct or "jpg" in ct else ".png" if "png" in ct else ".webp"
    path = f"/tmp/xhs_{tag}{ext}"
    with open(path, "wb") as f:
        f.write(r.content)
    return path, ct

def upload_body_img(token, path, mime):
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
    with open(path, "rb") as f:
        r = requests.post(url, files={"media": (os.path.basename(path), f, mime)}, timeout=20)
    r.encoding = "utf-8"
    data = r.json()
    if "url" not in data:
        raise Exception(f"上传正文图失败: {data}")
    return data["url"]

def upload_cover(token, path, mime):
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    with open(path, "rb") as f:
        r = requests.post(url, files={"media": (os.path.basename(path), f, mime)}, timeout=20)
    r.encoding = "utf-8"
    data = r.json()
    if "media_id" not in data:
        raise Exception(f"上传封面失败: {data}")
    return data["media_id"]

def body_to_html(body, img_urls):
    # 去掉纯 #标签 行
    lines = body.strip().split("\n")
    clean = []
    for line in lines:
        s = line.strip()
        if s and all(seg.startswith("#") or seg == "" for seg in re.split(r"\s+", s)):
            continue
        clean.append(line)
    body = "\n".join(clean).strip()

    paras = [p.strip() for p in body.split("\n") if p.strip()]
    p_style = 'style="font-size:16px;line-height:1.9;color:#333333;margin:0 0 14px;font-family:-apple-system,PingFang SC,sans-serif;"'
    img_style = 'style="max-width:100%;width:100%;height:auto;display:block;margin:16px 0;"'

    # 插图位置：首图在第1段后，其余均匀插入
    insert = {}
    if img_urls:
        insert.setdefault(1, []).append(img_urls[0])
        rest = img_urls[1:]
        if rest:
            step = max(2, len(paras) // (len(rest) + 1))
            for i, img in enumerate(rest):
                pos = min(1 + (i + 1) * step, len(paras))
                insert.setdefault(pos, []).append(img)

    parts = []
    for i, para in enumerate(paras):
        parts.append(f"<p {p_style}>{para}</p>")
        for img in insert.get(i + 1, []):
            parts.append(f'<img src="{img}" {img_style}/>')

    return "\n".join(parts)

def push_draft(token, title, html, thumb_media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    payload = {"articles": [{
        "title": title,
        "author": "周周在路上",
        "content": html,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }]}
    r = requests.post(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=20,
    )
    r.encoding = "utf-8"
    data = r.json()
    if "media_id" not in data:
        raise Exception(f"推送草稿失败: {data}")
    return data["media_id"]

def process_note(token, note, idx):
    print(f"\n{'='*52}")
    print(f"[{idx+1}] {note['title']}")
    imgs = note["images"]

    # 下载
    print(f"  ⬇ 下载 {len(imgs)} 张图片...")
    local = []
    for i, url in enumerate(imgs):
        path, mime = download_image(url, f"{idx}_{i}")
        local.append((path, mime))
        print(f"    图{i+1}: {os.path.getsize(path)//1024}KB")

    # 上传封面（永久）
    cover_path, cover_mime = local[0]
    print(f"  📌 上传封面...")
    thumb_id = upload_cover(token, cover_path, cover_mime)
    print(f"    media_id: {thumb_id[:32]}...")

    # 上传正文图（临时）
    print(f"  📤 上传正文图片...")
    wx_img_urls = []
    for path, mime in local:
        wx_url = upload_body_img(token, path, mime)
        wx_img_urls.append(wx_url)
        print(f"    OK: {wx_url[:55]}...")

    # 生成 HTML
    html = body_to_html(note["body"], wx_img_urls)

    # 推送草稿
    print(f"  🚀 推送草稿...")
    draft_id = push_draft(token, note["title"], html, thumb_id)
    print(f"  ✅ 成功! draft_id: {draft_id}")

    for path, _ in local:
        try: os.remove(path)
        except: pass

    return draft_id

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "notes_input.json"
    with open(input_file, encoding="utf-8") as f:
        notes = json.load(f)

    print(f"📋 共 {len(notes)} 篇笔记待推送")
    token = get_access_token()

    results = []
    for i, note in enumerate(notes):
        try:
            draft_id = process_note(token, note, i)
            results.append({"title": note["title"], "ok": True, "id": draft_id})
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            results.append({"title": note["title"], "ok": False, "err": str(e)})
        time.sleep(1)

    print(f"\n{'='*52}")
    print("📊 结果汇总:")
    for r in results:
        icon = "✅" if r["ok"] else "❌"
        print(f"  {icon} {r['title']}")
        if not r["ok"]:
            print(f"     → {r['err']}")

if __name__ == "__main__":
    main()
