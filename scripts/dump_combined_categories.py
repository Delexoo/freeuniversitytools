"""Dump tools in combined categories for splitting."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "student.html").read_text(encoding="utf-8")
SECTION_RE = re.compile(
    r'<section class="tool-category"[^>]*data-category="([^"]+)"[^>]*>.*?'
    r'<h3 class="category-title">([^<]*)</h3>.*?'
    r'<div class="category-tools">(.*?)</div>\s*</section>',
    re.DOTALL,
)
LINK_RE = re.compile(
    r'<a\s+href="([^"]+)"[^>]*>.*?<span class="tool-link-name">([^<]*)</span></a>',
    re.DOTALL,
)
for slug, title, block in SECTION_RE.findall(html):
    if " and " not in title.lower():
        continue
    print(f"\n=== {slug} | {title} ===")
    for url, name in LINK_RE.findall(block):
        print(f"  {name:40s} | {url}")
