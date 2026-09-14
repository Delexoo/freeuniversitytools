import json
import re
from pathlib import Path

tools = json.loads(Path("data/scroll-tools.json").read_text(encoding="utf-8"))
print("Microsoft store tools:")
for t in tools:
    u = (t.get("u") or "").lower()
    if "apps.microsoft.com" in u or "microsoft.com/store" in u:
        print(f"  {t['n']!r} | {t['u']}")

left = [t for t in tools if re.fullmatch(r"9[A-Za-z0-9]{11}", t.get("n", ""), re.I)]
print("leftover store-id names", len(left))
for t in left[:10]:
    print(t["n"], t["u"])

for t in tools:
    if "90DaysOfDevOps" in t.get("u", ""):
        print("devops name:", t["n"])
    if "90DaysOfCyber" in t.get("u", ""):
        print("cyber name:", t["n"])

ens = [t for t in tools if t.get("n") in ("En", "en", "Ai", "Pi")]
print("locale stub leftovers", len(ens))
for t in ens[:8]:
    print(t["n"], t["u"])
