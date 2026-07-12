"""Mirror a website locally using the website-downloader tool.

Usage:
  python scripts/mirror_site.py https://example.com
  python scripts/mirror_site.py https://example.com --render-js --max-pages 200
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DOWNLOADER = ROOT / "tools" / "website-downloader" / ".venv" / "Scripts" / "website-downloader.exe"
MIRRORS = ROOT / "mirrors"


def main() -> None:
    parser = argparse.ArgumentParser(description="Mirror a site for offline tool extraction.")
    parser.add_argument("url", help="Starting URL to crawl")
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument("--render-js", action="store_true", help="Use Playwright for JS-rendered sites")
    parser.add_argument("--sitemap", action="store_true", help="Seed crawl from sitemap.xml")
    parser.add_argument("--respect-robots", action="store_true")
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--destination", help="Output folder (default: mirrors/<host>)")
    args = parser.parse_args()

    if not DOWNLOADER.exists():
        print(
            "website-downloader is not installed.\n"
            "Run:\n"
            "  cd tools/website-downloader\n"
            "  python -m venv .venv\n"
            "  .venv\\Scripts\\pip install -e \".[fast,render]\"\n"
            "  .venv\\Scripts\\playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    host = urlparse(args.url).netloc.replace(":", "_")
    destination = Path(args.destination) if args.destination else MIRRORS / host
    destination.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(DOWNLOADER),
        "--url",
        args.url,
        "--destination",
        str(destination),
        "--max-pages",
        str(args.max_pages),
        "--delay",
        str(args.delay),
        "--respect-robots" if args.respect_robots else "",
    ]
    if args.render_js:
        cmd.append("--render-js")
    if args.sitemap:
        cmd.append("--sitemap")

    cmd = [part for part in cmd if part]
    print("Running:", " ".join(cmd))
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
