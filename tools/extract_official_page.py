#!/usr/bin/env python3
"""Isaac Sim 公式ドキュメントの HTML から本文を Markdown 風テキストとして抽出する。

WebFetch 等の要約系ツールはコードブロックが欠落するため、公式ページの正確な
本文・コードが必要な場合は必ずこのスクリプト（または curl + 手動確認）を使うこと。

使い方:
    python3 tools/extract_official_page.py <HTMLファイル | URL>

出力: 見出しは #、リスト項目は -、コードブロックは ``` フェンスで stdout に出力。
"""
import html
import re
import subprocess
import sys
import tempfile


def fetch(url: str) -> str:
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "60", url],
        capture_output=True, text=True, check=True,
    )
    return r.stdout


def extract(source: str) -> str:
    if source.startswith(("http://", "https://")):
        s = fetch(source)
    else:
        s = open(source, encoding="utf-8").read()
    m = re.search(r"<article[^>]*>(.*?)</article>", s, re.S)
    body = m.group(1) if m else s
    out = []
    for tag in re.finditer(r"<(h[1-6]|p|li|pre)[^>]*>(.*?)</\1>", body, re.S):
        name, inner = tag.group(1), tag.group(2)
        if name == "pre":
            t = html.unescape(re.sub(r"<[^>]+>", "", inner))
            out.append("```\n" + t.strip() + "\n```")
        else:
            t = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
            t = re.sub(r"\s+", " ", t)
            if t:
                prefix = "#" * int(name[1]) + " " if name.startswith("h") else "- " if name == "li" else ""
                out.append(prefix + t)
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    print(extract(sys.argv[1]))
