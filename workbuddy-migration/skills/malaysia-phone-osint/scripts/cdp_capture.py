#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用无头 Chrome + CDP 抓 JS 渲染页面的「真实接口」和「渲染后文本」。

原理: 页面是 React/Next.js 客户端渲染时, 静态 HTML 里没有数据。
      用浏览器真正跑一遍 JS, 同时监听 Network 域, 就能看到它到底调了哪个接口。

用法:
    python cdp_capture.py <url> [等待秒数]
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import requests
import websocket

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
PORT = 9333


def find_browser():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    raise SystemExit("找不到 Chrome/Edge")


def main():
    url = sys.argv[1]
    wait = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0

    profile = tempfile.mkdtemp(prefix="cdpcap_")
    proc = subprocess.Popen(
        [
            find_browser(),
            "--headless=new",
            f"--remote-debugging-port={PORT}",
            "--remote-allow-origins=*",
            f"--user-data-dir={profile}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-gpu",
            "--window-size=1280,900",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # 等调试端口就绪
        for _ in range(60):
            try:
                requests.get(f"http://127.0.0.1:{PORT}/json/version", timeout=1)
                break
            except Exception:
                time.sleep(0.5)
        else:
            raise SystemExit("调试端口未就绪")

        tab = requests.put(f"http://127.0.0.1:{PORT}/json/new?about:blank", timeout=5).json()
        ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=60)

        msg_id = [0]
        hits = []      # 捕获到的 XHR / Fetch
        responses = {}  # requestId -> url

        def send(method, params=None):
            msg_id[0] += 1
            ws.send(json.dumps({"id": msg_id[0], "method": method, "params": params or {}}))
            return msg_id[0]

        def pump(seconds):
            end = time.time() + seconds
            while time.time() < end:
                ws.settimeout(max(0.2, end - time.time()))
                try:
                    raw = ws.recv()
                except Exception:
                    break
                try:
                    m = json.loads(raw)
                except Exception:
                    continue
                method = m.get("method", "")
                p = m.get("params", {})
                if method == "Network.requestWillBeSent":
                    req = p.get("request", {})
                    if p.get("type") in ("XHR", "Fetch"):
                        hits.append((req.get("method"), req.get("url"),
                                     json.dumps(req.get("postData", ""))[:200]))
                        responses[p["requestId"]] = req.get("url")
                elif method == "Network.responseReceived":
                    responses.setdefault(p["requestId"], p.get("response", {}).get("url"))
                    if p["requestId"] in responses and p.get("response", {}).get("status", 0) >= 400:
                        pass

        send("Page.enable")
        send("Network.enable")
        send("Page.navigate", {"url": url})
        pump(wait)

        # 取渲染后的可见文本
        send("Runtime.enable")
        i = send("Runtime.evaluate", {
            "expression": "document.body ? document.body.innerText : ''",
            "returnByValue": True,
        })
        text = ""
        end = time.time() + 10
        while time.time() < end:
            ws.settimeout(5)
            try:
                m = json.loads(ws.recv())
            except Exception:
                break
            if m.get("id") == i:
                text = m.get("result", {}).get("result", {}).get("value", "") or ""
                break

        print("=" * 70)
        print("URL:", url)
        print("=" * 70)
        print("\n--- 捕获到的 XHR / Fetch 接口 ---")
        seen = set()
        for method, u, body in hits:
            key = (method, u)
            if key in seen:
                continue
            seen.add(key)
            print(f"{method:5} {u}")
            if body and body != '""':
                print(f"      body: {body}")
        if not hits:
            print("(未捕获到 XHR/Fetch —— 数据可能随服务端渲染一起下发)")

        print("\n--- 渲染后的可见文本（前 1500 字） ---")
        print(text[:1500] if text else "(空)")
        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
