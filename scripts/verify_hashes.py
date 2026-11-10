import hashlib, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parents[1]
rows = re.findall(r"\|\s*`([^`]+)`\s*\|\s*([0-9a-f]{64})\s*\|", (root / "HASHES.md").read_text())
failed = 0
for rel, expected in rows:
    p = root / rel
    ok = p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == expected
    print(("OK    " if ok else "FAIL  ") + rel)
    failed += not ok
print(f"{len(rows) - failed} of {len(rows)} frozen files match")
sys.exit(1 if failed else 0)
