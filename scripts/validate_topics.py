#!/usr/bin/env python3
"""Full validation of all topic JSON files across all sub-folders."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS_DIR = ROOT / "src" / "content" / "topics"
VALID_UNITS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
KNOWN_STUBS = {
    "caching", "docker", "firewalls", "ftp", "rate-limiting",
    "websockets", "fin-macroeconomics",
}

issues: list[str] = []
stats: list[str] = []

for p in sorted(TOPICS_DIR.rglob("*.json")):
    d = json.loads(p.read_text())
    name = p.name
    sid = d.get("id", p.stem)
    q_count = len(d.get("questions", []))
    fc_count = len(d.get("flashcards", []))
    g_len = len(d.get("guide", ""))
    required = {
        "id", "unit", "order", "title", "summary",
        "prereqs", "guide", "questions", "flashcards", "project",
    }
    missing = required - d.keys()
    is_stub = sid in KNOWN_STUBS

    if missing:
        issues.append(f"{name}: missing keys {sorted(missing)}")
    unit = d.get("unit")
    if unit not in VALID_UNITS:
        issues.append(f"{name}: unit={unit} not in valid set {VALID_UNITS}")

    for q in d.get("questions", []):
        for f in ("id", "type", "prompt", "explanation", "tags"):
            if f not in q:
                issues.append(f"{name}: question {q.get('id', '?')} missing '{f}'")
        if q.get("type") == "mcq" and "answerIndex" not in q:
            issues.append(f"{name}: mcq {q.get('id', '?')} missing answerIndex")
        if q.get("type") == "multi" and "answerIndexes" not in q:
            issues.append(f"{name}: multi {q.get('id', '?')} missing answerIndexes")

    if not is_stub:
        if q_count < 20:
            issues.append(f"{name}: only {q_count} questions (need 20)")
        if fc_count < 8:
            issues.append(f"{name}: only {fc_count} flashcards (need 8)")
        if g_len < 3000:
            issues.append(f"{name}: guide only {g_len} chars (need 3000+)")

    note = " [STUB]" if is_stub else ""
    ok = (
        not is_stub
        and not missing
        and q_count >= 20
        and fc_count >= 8
        and g_len >= 3000
        and unit in VALID_UNITS
    )
    mark = "OK" if ok else ("--" if is_stub else "!!")
    stats.append(
        f"  {mark} {name:48} {q_count:2}q {fc_count}fc {g_len:5}chars{note}"
    )

print(f"Topics scanned: {len(stats)}\n")
for s in stats:
    print(s)
print()
if issues:
    print(f"ISSUES FOUND: {len(issues)}")
    for i in issues:
        print("  ISSUE:", i)
else:
    print("ALL CHECKS PASSED — no structural issues found")


if __name__ == "__main__":
    pass
