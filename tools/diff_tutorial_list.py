#!/usr/bin/env python3
"""公式チュートリアル一覧（tutorial_list.html）のリンク集合を 2 バージョン間で比較する。

バージョン更新作業の最初に実行し、「削除されたページ」「追加されたページ」を洗い出す。
削除ページは MAINTENANCE.md の削除ページポリシーの対象、追加ページは新規作成候補になる。

使い方:
    python3 tools/diff_tutorial_list.py [--old 5.1.0] [--new latest]
"""
import argparse
import re
import subprocess

BASE = "https://docs.isaacsim.omniverse.nvidia.com"


def links(version: str) -> list[str]:
    url = f"{BASE}/{version}/introduction/tutorial_list.html"
    s = subprocess.run(["curl", "-sL", "--max-time", "60", url],
                       capture_output=True, text=True, check=True).stdout
    out, seen = [], set()
    for a in re.finditer(r'href="([^"]+)"', s):
        h = a.group(1).split("#")[0]
        if h.endswith(".html") and ("../" in h or h.startswith(("tutorial", "quickstart"))) \
                and "genindex" not in h:
            h = h.replace("../", "")
            if h not in seen:
                seen.add(h)
                out.append(h)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", default="5.1.0")
    ap.add_argument("--new", default="latest")
    args = ap.parse_args()

    old, new = links(args.old), links(args.new)
    old_set, new_set = set(old), set(new)
    print(f"# {args.old}: {len(old)} links / {args.new}: {len(new)} links")
    print(f"\n## {args.new} で削除されたページ（削除ページポリシー対象の可能性）")
    for x in old:
        if x not in new_set:
            print(f"- {x}")
    print(f"\n## {args.new} で追加されたページ（新規作成候補）")
    for x in new:
        if x not in old_set:
            print(f"- {x}")


if __name__ == "__main__":
    main()
