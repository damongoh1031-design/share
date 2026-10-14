#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create/renew a GitHub classic PAT using only username + password (no 2FA).

Writes the token to <skill>/token.txt and validates it against the API.
Usage:
  python mint_pat.py --user <email> --pass <password> [--days 90] [--note NAME]
  GITHUB_USER / GITHUB_PASS env vars are used when flags are omitted.
"""
import argparse
import http.cookiejar
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import gzip
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def fetch(url, data=None, referer=None, accept=None):
    r = urllib.request.Request(url, data=urllib.parse.urlencode(data, doseq=True).encode() if data else None)
    r.add_header("User-Agent", UA)
    r.add_header("Accept", accept or "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    if data:
        r.add_header("Content-Type", "application/x-www-form-urlencoded")
    if referer:
        r.add_header("Referer", referer)
    resp = op.open(r, timeout=40)
    raw = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    return resp.geturl(), raw.decode("utf-8", "replace")


def csrf(html):
    m = (re.search(r'name="authenticity_token"\s+value="([^"]+)"', html)
         or re.search(r'authenticity_token"[^>]*value="([^"]+)"', html))
    if not m:
        raise SystemExit("ERROR: authenticity_token not found")
    return m.group(1)


def test_token(tok):
    r = urllib.request.Request("https://api.github.com/user")
    r.add_header("User-Agent", UA)
    r.add_header("Authorization", "Bearer " + tok)
    r.add_header("Accept", "application/vnd.github+json")
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        return "OK login=%s" % json.loads(resp.read().decode()).get("login")
    except urllib.error.HTTPError as e:
        return "HTTP %s %s" % (e.code, e.read().decode()[:100].replace("\n", " "))
    except Exception as e:
        return "EXC %s" % e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_USER"))
    ap.add_argument("--pass", dest="password", default=os.environ.get("GITHUB_PASS"))
    ap.add_argument("--days", default="90")
    ap.add_argument("--note", default="github-sync-autopush")
    args = ap.parse_args()
    if not args.user or not args.password:
        sys.exit("ERROR: --user/--pass required (or GITHUB_USER/GITHUB_PASS)")

    _, h = fetch("https://github.com/login")
    fetch("https://github.com/session", {
        "login": args.user, "password": args.password, "authenticity_token": csrf(h),
        "commit": "Sign in", "webauthn-support": "supported",
        "webauthn-iuvpaa-support": "unsupported",
    }, "https://github.com/login")

    _, newp = fetch("https://github.com/settings/tokens/new", referer="https://github.com/settings/tokens")
    _, b = fetch("https://github.com/settings/tokens", [
        ("authenticity_token", csrf(newp)),
        ("oauth_access[description]", args.note),
        ("oauth_access[scopes][]", "repo"),
        # 关键：不传这一项，token 会「创建即过期」，API 一律 401 Bad credentials
        ("oauth_access[default_expires_at]", args.days),
    ], referer="https://github.com/settings/tokens/new")

    m = re.search(r"\b(ghp_[A-Za-z0-9]{30,})\b", b)
    if not m:
        sys.exit("ERROR: no token in response (login likely hit 2FA or CAPTCHA)")

    tok = m.group(1)
    result = test_token(tok)
    if not result.startswith("OK"):
        sys.exit("ERROR: token invalid -> %s" % result)

    (SKILL_DIR / "token.txt").write_text(tok + "\n", encoding="utf-8")
    print("TOKEN written to %s | scope=repo | expires in %s days | %s"
          % (SKILL_DIR / "token.txt", args.days, result))


if __name__ == "__main__":
    main()
