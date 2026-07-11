"""Export unique hosts and current pricing for research."""
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "student.html").read_text(encoding="utf-8")
LINK_RE = re.compile(
    r'data-category="([^"]+)".*?<div class="category-tools">(.*?)</div>\s*</section>',
    re.DOTALL,
)
INNER = re.compile(
    r'href="([^"]+)"[^>]*data-pricing="([^"]+)"[^>]*>.*?'
    r'<span class="tool-link-name">([^<]+)</span>',
    re.DOTALL,
)

by_host = defaultdict(lambda: defaultdict(int))
for sec in LINK_RE.finditer(html):
    cat = sec.group(1)
    for m in INNER.finditer(sec.group(2)):
        url, pricing, name = m.group(1), m.group(2), m.group(3).strip()
        host = urlparse(url).netloc.lower().replace("www.", "")
        by_host[host][pricing] += 1

lines = []
for host, counts in sorted(by_host.items(), key=lambda x: -sum(x[1].values())):
    total = sum(counts.values())
    dist = ", ".join(f"{k}:{v}" for k, v in sorted(counts.items()))
    lines.append(f"{host}\t{total}\t{dist}")

out = ROOT / "scripts" / "pricing_hosts.tsv"
out.write_text("host\ttotal\tdistribution\n" + "\n".join(lines), encoding="utf-8")
print(f"Wrote {len(by_host)} hosts to {out}")
