#!/usr/bin/env python3
"""docs/**/*.md 内の外部 URL がすべて 200 を返すか検証する。

バージョン更新・大規模編集の仕上げに必ず実行すること。
デフォルトでは公式ドキュメント（docs.isaacsim.omniverse.nvidia.com）の URL のみを
対象とする。--all で全ドメインを対象にする（GitHub 等は rate limit に注意）。

使い方:
    python3 tools/check_links.py [--all] [--workers 12]

終了コード: 全て 200 なら 0、非 200 が 1 件でもあれば 1。
"""
import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"
OFFICIAL = re.compile(r"https://docs\.isaacsim\.omniverse\.nvidia\.com[^\s)\"'<>\]]+")
ANY_URL = re.compile(r"https?://[^\s)\"'<>\]]+")


def head(url: str) -> tuple[str, str]:
    r = subprocess.run(
        ["curl", "-sL", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20", url],
        capture_output=True, text=True,
    )
    return url, r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="公式ドキュメント以外の URL も検証する")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    pat = ANY_URL if args.all else OFFICIAL
    url_files: dict[str, set[str]] = {}
    for f in DOCS.rglob("*.md"):
        for m in pat.finditer(f.read_text(encoding="utf-8")):
            u = m.group(0).rstrip(".,;:")
            url_files.setdefault(u, set()).add(str(f.relative_to(REPO_ROOT)))

    urls = sorted(url_files)
    print(f"{len(urls)} unique URLs", file=sys.stderr)

    bad = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for u, code in ex.map(head, urls):
            if code != "200":
                bad.append((u, code))
                print(f"{code} {u}")
                for f in sorted(url_files[u]):
                    print(f"    in {f}")

    print(f"\n{len(bad)} bad / {len(urls)} total", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
