import re
from pathlib import Path

html = (Path(__file__).parent.parent / "student.html").read_text(encoding="utf-8")
js = (Path(__file__).parent.parent / "js" / "student.js").read_text(encoding="utf-8")

cats = re.findall(r'<section class="tool-category" data-category="([^"]+)"', html)
links = len(re.findall(r'class="tool-link"', html))
kw = re.findall(r"'([a-z0-9-]+)':\s*\[", js)
kw_set = set(kw)

print(f"categories in HTML: {len(cats)} (unique: {len(set(cats))})")
print(f"tool links: {links}")
print(f"CATEGORY_KEYWORDS entries: {len(kw_set)}")
missing = set(cats) - kw_set
extra = kw_set - set(cats)
if missing:
    print(f"missing keywords: {sorted(missing)}")
if extra:
    print(f"extra keywords (no section): {sorted(extra)}")
