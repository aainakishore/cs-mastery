#!/usr/bin/env python3
"""
Reorganize all topic JSONs:
 - Reassign unit numbers (beginner → hard ordering)
 - Fix order numbers (unique, sequential within unit)
 - Move files to correct sub-folders
 - Create new folders as needed

New unit structure:
 Unit 1  Foundations          beginner
 Unit 2  Python               beginner
 Unit 3  TypeScript           intermediate
 Unit 4  React                intermediate
 Unit 5  Angular              intermediate
 Unit 6  Networking           intermediate
 Unit 7  AI Primer            intermediate
 Unit 8  DSA in Java          advanced
 Unit 9  Scaling & Data       advanced
 Unit 10 Cloud & DevOps       advanced
 Unit 11 AI Advanced          advanced
 Unit 12 Security             advanced
 Unit 13 System Design        expert
 Unit 14 Java Advanced        expert
 Unit 15 Financial Literacy   optional
 Unit 16 Advanced Engineering optional
 Unit 17 Tooling              optional

Run: python3 scripts/reorganize_units.py
"""

import json, shutil
from pathlib import Path

BASE = Path(__file__).parent.parent / "src/content/topics"

# -------------------------------------------------------------------
# Define every topic: (current_id, new_unit, new_order, new_folder)
# order is global unique across all topics
# -------------------------------------------------------------------
TOPIC_MAP = {
    # UNIT 1 — Foundations (orders 1-10)
    "linux-essentials":        (1,  1,  "foundations"),
    "git-fundamentals":        (1,  2,  "foundations"),
    "relational-databases-sql":(1,  3,  "foundations"),
    "embedded-databases":      (1,  4,  "foundations"),
    "time-space-complexity":   (1,  5,  "foundations"),
    "recursion-mental-model":  (1,  6,  "foundations"),
    "memory-stack-heap":       (1,  7,  "foundations"),
    "pointers-references":     (1,  8,  "foundations"),
    # duplicates in scaling folder — skip (handled by dedup below)
    "relational-databases":    (1,  3,  "foundations"),   # duplicate of relational-databases-sql
    "embedded-databases":      (1,  4,  "foundations"),   # duplicate

    # UNIT 2 — Python (orders 11-19)
    "python-fundamentals":     (2, 11,  "python"),
    "python-oop":              (2, 12,  "python"),
    "python-error-handling":   (2, 13,  "python"),
    "python-functional":       (2, 14,  "python"),
    "python-type-hints":       (2, 15,  "python"),

    # UNIT 3 — TypeScript (orders 20-27)
    "ts-fundamentals":         (3, 20,  "typescript"),
    "ts-interfaces-types":     (3, 21,  "typescript"),
    "ts-generics":             (3, 22,  "typescript"),
    "ts-utility-types":        (3, 23,  "typescript"),
    "ts-advanced-types":       (3, 24,  "typescript"),
    "ts-decorators":           (3, 25,  "typescript"),
    "ts-modules":              (3, 26,  "typescript"),
    "ts-tsconfig":             (3, 27,  "typescript"),

    # UNIT 4 — React (orders 28-36)
    "react-fundamentals":      (4, 28,  "react"),
    "react-state-effects":     (4, 29,  "react"),
    "react-hooks":             (4, 30,  "react"),
    "react-context":           (4, 31,  "react"),
    "react-rendering":         (4, 32,  "react"),
    "react-router":            (4, 33,  "react"),
    "react-forms":             (4, 34,  "react"),
    "react-performance":       (4, 35,  "react"),
    "react-server-components": (4, 36,  "react"),

    # UNIT 5 — Angular (orders 37-45)
    "angular-fundamentals":    (5, 37,  "angular"),
    "angular-data-binding":    (5, 38,  "angular"),
    "angular-directives":      (5, 39,  "angular"),
    "angular-services-di":     (5, 40,  "angular"),
    "angular-rxjs":            (5, 41,  "angular"),
    "angular-routing":         (5, 42,  "angular"),
    "angular-forms":           (5, 43,  "angular"),
    "angular-signals":         (5, 44,  "angular"),
    "angular-standalone":      (5, 45,  "angular"),

    # UNIT 6 — Networking (orders 46-54)
    "firewalls":               (6, 46,  "networking"),
    "ftp":                     (6, 47,  "networking"),
    "proxies":                 (6, 48,  "networking"),
    "rpc":                     (6, 49,  "networking"),
    "websockets":              (6, 50,  "networking"),
    "long-polling":            (6, 51,  "networking"),
    "rate-limiting":           (6, 52,  "networking"),
    "qps-capacity":            (6, 53,  "networking"),
    "load-balancing":          (6, 54,  "networking"),

    # UNIT 7 — AI Primer (orders 55-59)
    "ml-basics":               (7, 55,  "ai"),
    "neural-nets":             (7, 56,  "ai"),
    "transformers":            (7, 57,  "ai"),
    "llms":                    (7, 58,  "ai"),
    "prompting-fundamentals":  (7, 59,  "ai"),

    # UNIT 8 — DSA in Java (orders 60-79)
    "dsa-java-arrays":         (8, 60,  "dsa-java"),
    "dsa-java-strings":        (8, 61,  "dsa-java"),
    "dsa-java-linked-lists":   (8, 62,  "dsa-java"),
    "dsa-java-stacks":         (8, 63,  "dsa-java"),
    "dsa-java-queues":         (8, 64,  "dsa-java"),
    "dsa-java-hashing":        (8, 65,  "dsa-java"),
    "dsa-java-recursion":      (8, 66,  "dsa-java"),
    "dsa-java-sorting":        (8, 67,  "dsa-java"),
    "dsa-java-searching":      (8, 68,  "dsa-java"),
    "dsa-java-binary-trees":   (8, 69,  "dsa-java"),
    "dsa-java-trees":          (8, 70,  "dsa-java"),
    "dsa-java-heaps":          (8, 71,  "dsa-java"),
    "dsa-java-graphs-basics":  (8, 72,  "dsa-java"),
    "dsa-java-graphs-advanced":(8, 73,  "dsa-java"),
    "dsa-java-dp-intro":       (8, 74,  "dsa-java"),
    "dsa-java-dp-sequences":   (8, 75,  "dsa-java"),
    "dsa-java-tries":          (8, 76,  "dsa-java"),
    "dsa-java-sliding-window": (8, 77,  "dsa-java"),
    "dsa-java-two-pointers":   (8, 78,  "dsa-java"),

    # UNIT 9 — Scaling & Data (orders 80-85)
    "caching":                 (9, 80,  "scaling"),
    "sharding":                (9, 81,  "scaling"),
    "partitioning":            (9, 82,  "scaling"),
    "kafka":                   (9, 83,  "scaling"),
    "rabbitmq":                (9, 84,  "scaling"),
    "aws-sqs":                 (9, 85,  "scaling"),

    # UNIT 10 — Cloud & DevOps (orders 86-93)
    "cloud-fundamentals":      (10, 86, "cloud-devops"),
    "docker":                  (10, 87, "cloud-devops"),
    "kubernetes":              (10, 88, "cloud-devops"),
    "aws-practitioner":        (10, 89, "cloud-devops"),
    "aws-mastery":             (10, 90, "cloud-devops"),
    "serverless-patterns":     (10, 91, "cloud-devops"),
    "cicd-pipelines":          (10, 92, "cloud-devops"),
    "error-logging":           (10, 93, "cloud-devops"),

    # UNIT 11 — AI Advanced (orders 94-100)
    "agents":                  (11, 94, "ai"),
    "rag":                     (11, 95, "ai"),
    "fine-tuning":             (11, 96, "ai"),
    "leverage-strategies":     (11, 97, "ai"),
    "ai-image-generation":     (11, 98, "ai"),
    "prompt-engineering-advanced": (11, 99, "ai"),
    "llm-ops":                 (11, 100,"ai"),

    # UNIT 12 — Security (orders 101-101)
    "security-fundamentals":   (12, 101,"security"),

    # UNIT 13 — System Design (orders 102-107)
    "system-design-fundamentals":  (13, 102, "system-design"),
    "data-structures-advanced":    (13, 103, "system-design"),
    "distributed-systems":         (13, 104, "system-design"),
    "database-internals":          (13, 105, "system-design"),
    "observability":               (13, 106, "system-design"),

    # UNIT 14 — Java Advanced (orders 107-110) — stubs, filled by gen script
    # (no existing topics — created by gen_java_advanced_batch1.py)

    # UNIT 15 — Financial Literacy (orders 111-117)
    "fin-stock-market-basics":  (15, 111, "finance"),
    "fin-technical-analysis":   (15, 112, "finance"),
    "fin-fundamental-analysis": (15, 113, "finance"),
    "fin-options-basics":       (15, 114, "finance"),
    "fin-mutual-funds":         (15, 115, "finance"),
    "fin-personal-finance":     (15, 116, "finance"),
    "fin-macroeconomics":       (15, 117, "finance"),

    # UNIT 16 — Advanced Engineering (orders 118-119)
    "sql-advanced":             (16, 118, "advanced"),
    "git-advanced":             (16, 119, "advanced"),

    # UNIT 17 — Tooling (orders 120)
    "pycharm":                  (17, 120, "cloud-devops"),
}


def reorganize():
    # Create all needed folders
    new_folders = set(v[2] for v in TOPIC_MAP.values())
    new_folders.add("system-design")
    new_folders.add("python")
    new_folders.add("advanced")
    for f in new_folders:
        (BASE / f).mkdir(exist_ok=True)

    # Collect all existing JSON files by id
    existing: dict[str, Path] = {}
    for p in BASE.rglob("*.json"):
        try:
            d = json.loads(p.read_text())
            tid = d.get("id")
            if tid:
                if tid in existing:
                    # Keep the one with more questions (better version)
                    d2 = json.loads(existing[tid].read_text())
                    if len(d.get("questions", [])) > len(d2.get("questions", [])):
                        existing[tid] = p
                else:
                    existing[tid] = p
        except Exception as e:
            print(f"  WARN: could not parse {p}: {e}")

    moved = 0
    updated = 0
    skipped = 0

    for tid, (new_unit, new_order, new_folder) in TOPIC_MAP.items():
        if tid not in existing:
            skipped += 1
            continue

        src = existing[tid]
        d = json.loads(src.read_text())

        changed = False
        if d.get("unit") != new_unit:
            d["unit"] = new_unit
            changed = True
        if d.get("order") != new_order:
            d["order"] = new_order
            changed = True

        dest_dir = BASE / new_folder
        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / f"{tid}.json"

        if src != dest:
            dest.write_text(json.dumps(d, indent=2, ensure_ascii=False))
            if src.exists():
                src.unlink()
            print(f"  MOVED  {tid} → {new_folder}/ (unit {new_unit}, order {new_order})")
            moved += 1
        elif changed:
            dest.write_text(json.dumps(d, indent=2, ensure_ascii=False))
            print(f"  UPDATE {tid} (unit {new_unit}, order {new_order})")
            updated += 1

    # Clean up empty source folders
    for folder in BASE.iterdir():
        if folder.is_dir():
            remaining = list(folder.glob("*.json"))
            if not remaining:
                try:
                    folder.rmdir()
                    print(f"  RMDIR  {folder.name}/")
                except:
                    pass

    print(f"\n✓ Moved: {moved}, Updated: {updated}, Skipped (not found): {skipped}")


if __name__ == "__main__":
    print("Reorganizing topic files...")
    reorganize()
    print("Done.")

