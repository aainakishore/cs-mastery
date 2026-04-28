"""
consolidate_scripts.py
Merges all scattered patch_*.py topic-writer scripts into one file per section.
Sections produced:
  patch_cloud_devops.py  — linux, git, docker, k8s, cicd, cloud, aws, serverless, pycharm
  patch_networking.py    — firewalls, ftp, proxies, rpc, websockets, polling, rate-limiting, qps, load-balancing, kafka, rabbitmq
  patch_scaling.py       — caching, sharding, partitioning, kafka (scaling view), rabbitmq (scaling view), sqs
  patch_ai.py            — all ai/ folder guides
  patch_frontend.py      — angular, react, typescript guides

This script itself does NOT re-run the patches — it only produces the consolidated files
by copying the patch logic from each source file.

Run: python3 scripts/consolidate_scripts.py
"""
import subprocess
from pathlib import Path

SCRIPTS = Path(__file__).parent

# Map: consolidated filename → list of source patch files to include (in order)
GROUPS = {
    "patch_cloud_devops.py": [
        "patch_linux.py",
        "patch_git.py",
        "patch_docker.py",
        "patch_k8s.py",
        "patch_cicd.py",
        "patch_cloud.py",
        "patch_aws_prac.py",
        "patch_aws_mastery.py",
        "patch_serverless.py",
        "patch_serverless_fix.py",
        "patch_sls_final.py",
        "patch_pycharm.py",
    ],
    "patch_networking.py": [
        "patch_networking_1.py",
        "patch_networking_2.py",
        "patch_networking_3.py",
        "patch_ws_extra.py",
        "fix_ftp_guide.py",
    ],
    "patch_scaling.py": [
        "patch_scaling_1.py",
        "patch_scaling_2.py",
        "patch_scaling_3.py",
        "patch_sqs.py",
    ],
    "patch_ai.py": [
        "patch_ai_guides.py",
    ],
    "patch_foundations.py": [
        "foundations_batch1.py",
        "foundations_batch2a.py",
        "foundations_batch2b.py",
    ],
    "patch_guides_all.py": [
        "patch_guides.py",
        "patch_guides_1.py",
        "patch_guides_2.py",
        "patch_guides_3.py",
        "patch_guides_4.py",
        "patch_short_guides.py",
    ],
}

HEADER = '''"""
{title}
Consolidated from: {sources}
Run: python3 scripts/{fname}
Each section is clearly delimited — you can copy/edit individual sections.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent / "src/content/topics"


def patch(folder, filename, updates):
    p = BASE / folder / filename
    if not p.exists():
        print(f"  SKIP (not found): {{folder}}/{{filename}}")
        return
    d = json.loads(p.read_text())
    before_q = len(d.get("questions", []))
    d.update(updates)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print(f"  OK {{filename}}: guide={{len(d.get('guide',''))}} q={{len(d.get('questions',[]))}} fc={{len(d.get('flashcards',[]))}}")


def main():
'''

def extract_body(src: Path) -> str:
    """Extract the actual patch body from a source file, excluding its own header/imports."""
    lines = src.read_text().splitlines()
    body = []
    in_body = False
    for line in lines:
        if not in_body:
            # Skip until after imports and module-level boilerplate
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from ") or stripped.startswith("#") or stripped == "":
                continue
            else:
                in_body = True
        body.append(line)
    return "\n".join(body)


for out_name, sources in GROUPS.items():
    src_paths = [SCRIPTS / s for s in sources]
    existing = [p for p in src_paths if p.exists()]
    missing = [s for s, p in zip(sources, src_paths) if not p.exists()]
    if missing:
        print(f"  WARNING: {out_name}: missing sources: {missing}")

    bodies = []
    for p in existing:
        bodies.append(f"\n    # ── {p.name} ──────────────────────────────────────────────────────────────────")
        body = extract_body(p)
        # indent everything 4 spaces for inside main()
        indented = "\n".join("    " + l if l.strip() else "" for l in body.splitlines())
        bodies.append(indented)

    content = HEADER.format(
        title=out_name.replace(".py","").replace("_"," ").title() + " — Consolidated Patch Script",
        sources=", ".join(sources),
        fname=out_name,
    )
    content += "\n".join(bodies)
    content += "\n\nif __name__ == '__main__':\n    main()\n"

    out_path = SCRIPTS / out_name
    out_path.write_text(content)
    print(f"WROTE {out_name} ({len(existing)}/{len(sources)} sources merged, {len(content)} chars)")

print("\nDone! Consolidated scripts created.")
print("Old patch_*.py files kept intact — safe to delete once you verify the consolidated ones work.")
print("")
print("Run any section:")
print("  python3 scripts/patch_cloud_devops.py")
print("  python3 scripts/patch_networking.py")
print("  python3 scripts/patch_scaling.py")
print("  python3 scripts/patch_ai.py")
print("  python3 scripts/patch_foundations.py")

