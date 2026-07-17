#!/usr/bin/env python3
"""Isaac Sim 公式ドキュメントの同一ページを 2 バージョン間で diff する。

バージョン更新作業の中心ツール。各チュートリアルページについて旧バージョンと
新バージョン（latest）の本文・コードの差分を確認し、本サイトへ反映する差分の
根拠（グラウンドトゥルース）とする。

使い方:
    python3 tools/diff_official_page.py <ページパス> [--old 5.1.0] [--new latest]

例:
    python3 tools/diff_official_page.py core_api_tutorials/tutorial_core_hello_world.html
    python3 tools/diff_official_page.py ros2_tutorials/tutorial_ros2_tf.html --old 6.0.1 --new latest

ページが新バージョンで 404 の場合はその旨を表示する（削除ページポリシーの対象）。
"""
import argparse
import difflib
import subprocess
import sys

from extract_official_page import extract

BASE = "https://docs.isaacsim.omniverse.nvidia.com"


def status(url: str) -> str:
    r = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "30", url],
        capture_output=True, text=True,
    )
    return r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", help="バージョン以下のページパス（例: core_api_tutorials/tutorial_core_hello_world.html）")
    ap.add_argument("--old", default="5.1.0", help="旧バージョン（デフォルト: 5.1.0）")
    ap.add_argument("--new", default="latest", help="新バージョン（デフォルト: latest）")
    args = ap.parse_args()

    page = args.page.lstrip("/")
    old_url = f"{BASE}/{args.old}/{page}"
    new_url = f"{BASE}/{args.new}/{page}"

    for label, url in (("old", old_url), ("new", new_url)):
        code = status(url)
        print(f"[{label}] {code} {url}", file=sys.stderr)
        if code != "200":
            if label == "new":
                print(f"\n*** {args.new} で {code}：削除または移転の可能性。"
                      f"introduction/tutorial_list.html で移転先を探すこと ***")
                return 1
            print(f"*** 旧バージョン側が {code}。ページパスを確認してください ***", file=sys.stderr)
            return 2

    old_text = extract(old_url).splitlines()
    new_text = extract(new_url).splitlines()
    diff = list(difflib.unified_diff(old_text, new_text,
                                     fromfile=f"{args.old}/{page}",
                                     tofile=f"{args.new}/{page}", lineterm=""))
    if not diff:
        print("（本文・コードの差分なし。画像 URL やリンクのバージョン置換のみ確認すればよい）")
        return 0
    print("\n".join(diff))
    return 0


if __name__ == "__main__":
    sys.exit(main())
