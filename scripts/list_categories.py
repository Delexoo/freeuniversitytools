"""List all tool categories in student.html."""
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
LINK_RE = re.compile(r'<span class="tool-link-name">([^<]*)</span>')
for slug, title, block in SECTION_RE.findall(html):
    count = len(LINK_RE.findall(block))
    marker = " *** COMBINED ***" if " and " in title.lower() else ""
    print(f"{count:4d} | {slug:30s} | {title}{marker}")
