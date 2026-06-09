#!/usr/bin/env python3
"""
push_kraft.py — 牛皮纸风格HTML推送到微信公众号草稿箱
1. 读取HTML文件
2. 把<style>里的CSS转成所有元素的内联style
3. 上传正文图片到微信素材库
4. 上传封面图（永久素材）
5. 推送草稿
"""

import json, re, sys, time, urllib.request, urllib.parse, pathlib

# ── 配置 ──────────────────────────────────────────────
APPID  = "wxb32d492616da4383"
SECRET = "a6831decfa9886bb06ea5c22ef6eb9cd"
HTML_FILE = pathlib.Path("/home/node/.openclaw/workspace/skills/wewrite-geo/output/demo-牛皮纸风格.html")
TITLE  = "用圆周旅迹规划俄罗斯（上）：莫斯科五天行程完整攻略"
AUTHOR = "圆周旅迹"
DIGEST = "签证怎么办、景点怎么串、地铁怎么坐，莫斯科五天完整攻略，附预算参考。"

# ── 工具函数 ──────────────────────────────────────────

def get_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={SECRET}"
    with urllib.request.urlopen(url, timeout=15) as r:
        r.encoding = "utf-8"
        data = json.loads(r.read().decode("utf-8"))
    if "access_token" not in data:
        raise RuntimeError(f"token失败: {data}")
    print(f"✅ token: {data['access_token'][:20]}...")
    return data["access_token"]

def upload_img_url(token, img_url):
    """下载图片URL并上传到微信uploadimg（临时素材，用于正文）"""
    # 下载图片
    req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        img_data = r.read()
    # 上传
    boundary = "----WeChatBoundary"
    filename = "photo.jpg"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="media"; filename="{filename}"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode() + img_data + f"\r\n--{boundary}--\r\n".encode()
    upload_url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
    req2 = urllib.request.Request(
        upload_url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req2, timeout=30) as r:
        resp = json.loads(r.read().decode("utf-8"))
    if "url" not in resp:
        print(f"  ⚠️  uploadimg失败: {resp}，保留原URL")
        return img_url
    print(f"  ✅ 正文图片上传成功: {resp['url'][:60]}")
    return resp["url"]

def upload_cover(token, img_url):
    """上传封面图到永久素材（add_material），返回media_id"""
    req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        img_data = r.read()
    boundary = "----WeChatBoundary2"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="media"; filename="cover.jpg"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode() + img_data + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="description"\r\n\r\n'
        f'{{}}\r\n--{boundary}--\r\n'
    ).encode()
    upload_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    req2 = urllib.request.Request(
        upload_url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req2, timeout=30) as r:
        resp = json.loads(r.read().decode("utf-8"))
    if "media_id" not in resp:
        raise RuntimeError(f"封面上传失败: {resp}")
    print(f"  ✅ 封面media_id: {resp['media_id']}")
    return resp["media_id"]

def inline_css(html: str) -> str:
    """
    把<style>中的CSS规则转成对应元素的内联style。
    采用简单正则方案：提取class→style映射，逐一替换。
    公众号会剥离<style>标签，所以必须内联。
    """
    # 提取style块
    style_match = re.search(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    if not style_match:
        return html
    css_text = style_match.group(1)

    # 解析 .classname { ... } 规则（只处理class选择器，够用了）
    class_styles = {}
    for m in re.finditer(r'\.([\w-]+)\s*\{([^}]+)\}', css_text):
        cls = m.group(1)
        props = m.group(2).strip()
        # 清理注释
        props = re.sub(r'/\*.*?\*/', '', props, flags=re.DOTALL).strip()
        if props:
            class_styles[cls] = props

    # 对每个有class的标签，把对应CSS合并进style属性
    def replace_tag(m):
        tag_str = m.group(0)
        classes_match = re.search(r'class=["\']([^"\']+)["\']', tag_str)
        if not classes_match:
            return tag_str
        classes = classes_match.group(1).split()
        merged = []
        for cls in classes:
            if cls in class_styles:
                merged.append(class_styles[cls])
        if not merged:
            return tag_str
        extra = " ".join(merged)
        # 如果已有style属性，追加；否则新增
        if 'style=' in tag_str:
            tag_str = re.sub(r'style=["\']([^"\']*)["\']',
                             lambda s: f'style="{s.group(1)}; {extra}"', tag_str)
        else:
            tag_str = tag_str.rstrip('>') + f' style="{extra}">'
            # 处理自闭合标签
            if tag_str.endswith('/>') or tag_str.endswith('" />'):
                pass
        return tag_str

    # 处理所有开标签
    html = re.sub(r'<[a-zA-Z][^>]*>', replace_tag, html)
    # 移除<style>块（公众号会忽略，但清掉更干净）
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    return html

def replace_images(token, html: str):
    """找出所有img src的pexels链接，上传到微信，替换成微信URL"""
    img_urls = re.findall(r'src=["\'](https://images\.pexels\.com[^"\']+)["\']', html)
    url_map = {}
    for i, url in enumerate(img_urls):
        if url in url_map:
            continue
        print(f"  上传图片 {i+1}/{len(img_urls)}: {url[:60]}...")
        if i == 0:
            # 第一张是封面，用add_material，正文也要一份uploadimg
            try:
                wx_url = upload_img_url(token, url)
                url_map[url] = wx_url
            except Exception as e:
                print(f"  ⚠️ 跳过: {e}")
                url_map[url] = url
        else:
            try:
                wx_url = upload_img_url(token, url)
                url_map[url] = wx_url
            except Exception as e:
                print(f"  ⚠️ 跳过: {e}")
                url_map[url] = url
        time.sleep(0.5)
    for orig, new in url_map.items():
        html = html.replace(orig, new)
    return html, img_urls[0] if img_urls else None

def push_draft(token, title, author, digest, content, cover_media_id):
    payload = {
        "articles": [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "thumb_media_id": cover_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }]
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read().decode("utf-8"))
    if resp.get("errcode", 0) != 0:
        raise RuntimeError(f"推送失败: {resp}")
    print(f"✅ 草稿推送成功！media_id: {resp.get('media_id')}")
    return resp

# ── 主流程 ────────────────────────────────────────────

def main():
    print("=== 圆周旅迹公众号推送脚本（牛皮纸风格）===\n")

    html = HTML_FILE.read_text(encoding="utf-8")
    print(f"✅ 读取HTML: {len(html)} 字节")

    # 1. 获取token
    token = get_token()

    # 2. 上传正文图片（替换Pexels链接）
    print("\n📸 上传正文图片...")
    html, cover_url = replace_images(token, html)

    # 3. 内联CSS
    print("\n🎨 内联CSS...")
    html = inline_css(html)
    print(f"  内联后HTML: {len(html)} 字节")

    # 4. 提取body内容（公众号只要body内的HTML）
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    content = body_match.group(1).strip() if body_match else html

    # 5. 上传封面图（永久素材）
    print("\n🖼️  上传封面图...")
    if cover_url:
        cover_media_id = upload_cover(token, cover_url)
    else:
        raise RuntimeError("没有找到封面图URL")

    # 6. 推送草稿
    print("\n🚀 推送草稿到微信公众号...")
    push_draft(token, TITLE, AUTHOR, DIGEST, content, cover_media_id)
    print("\n✅ 完成！请前往微信公众号后台 → 草稿箱 查看。")

if __name__ == "__main__":
    main()
