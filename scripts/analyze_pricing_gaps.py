"""List tools without pricing_engine rules and pricing distribution."""
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
from pricing_engine import resolve_pricing, load_base_rules, SECTION_RE, LINK_RE, NAME_RE

html = (ROOT / "student.html").read_text(encoding="utf-8")
rules = load_base_rules()

no_rule = []
for sec in SECTION_RE.finditer(html):
    cat = sec.group(1)
    for m in LINK_RE.finditer(sec.group(2)):
        full = m.group(0)
        url = m.group(2)
        pricing = m.group(4)
        name_m = NAME_RE.search(full)
        name = name_m.group(1).strip() if name_m else url
        exp = resolve_pricing(url, cat, rules, name)
        if exp is None:
            from pricing_engine import host_key

            no_rule.append((name, pricing, url, host_key(url)))

print(f"No pricing rule: {len(no_rule)}")
print("Distribution:", dict(Counter(x[1] for x in no_rule)))

hosts = defaultdict(list)
for name, pricing, url, host in no_rule:
    hosts[host].append((name, pricing, url))

print(f"\nUnique hosts without rules: {len(hosts)}")
for host, items in sorted(hosts.items(), key=lambda x: -len(x[1]))[:50]:
    sample = items[0]
    print(f"  {host} ({len(items)}) [{sample[1]}] {sample[0]}")
