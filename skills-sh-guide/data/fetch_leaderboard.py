"""抓取并解析 skills.sh 三张榜单（All Time / Trending / Hot）
可复跑：python fetch_leaderboard.py
输出：leaderboard.json（排名 + owner/repo/skill + 安装量）
"""
import re, json, html, urllib.request, sys, os

BOARDS = {
    "all_time": "https://www.skills.sh/",
    "trending": "https://www.skills.sh/trending",
    "hot": "https://www.skills.sh/hot",
}

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-bot",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", errors="ignore")

def parse(h):
    """从服务端渲染的 HTML 提取 <a href="/owner/repo/skill"> 条目与其安装量"""
    h2 = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S)
    parts = re.split(
        r'(?=<a[^>]+href="/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+")', h2)
    out, seen = [], set()
    for p in parts:
        m = re.match(r'<a[^>]+href="(/[^"]+)"', p)
        if not m:
            continue
        href = m.group(1)
        if href.count("/") != 3 or href.startswith("/site"):
            continue
        if href in seen:
            continue
        seen.add(href)
        nums = re.findall(
            r'class="font-mono text-sm text-foreground">([0-9.]+[KM]?)<', p)
        out.append((href, nums[0] if nums else None))
    return out

def main():
    result = {}
    for name, url in BOARDS.items():
        try:
            h = fetch(url)
            rows = parse(h)
            result[name] = [
                {"rank": i, "owner": hh.strip("/").split("/")[0],
                 "repo": hh.strip("/").split("/")[1],
                 "skill": hh.strip("/").split("/")[2],
                 "value": v, "url": "https://www.skills.sh" + hh}
                for i, (hh, v) in enumerate(rows, 1)
            ]
            print(f"[{name}] {len(result[name])} entries")
        except Exception as e:
            print(f"[{name}] ERROR {e}", file=sys.stderr)
            result[name] = []

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard-raw.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("saved ->", out_path)

if __name__ == "__main__":
    main()
