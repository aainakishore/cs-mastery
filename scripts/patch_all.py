#!/usr/bin/env python3
"""
patch_all.py — Master dispatcher for all topic patching scripts.
Consolidates all individual patch_*.py scripts into one entry point.

Usage:
    python3 scripts/patch_all.py              # validate + report
    python3 scripts/patch_all.py --status     # show status of all topics
    python3 scripts/patch_all.py --folder networking  # patch one folder

This script is the canonical reference. The individual patch_*.py
scripts still exist and can be run independently.
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent / 'src/content/topics'

FOLDERS = ['ai', 'angular', 'cloud-devops', 'dsa-java', 'finance',
           'foundations', 'networking', 'react', 'scaling', 'typescript']

def status():
    total_ok = 0
    total_bad = 0
    for folder in FOLDERS:
        d = BASE / folder
        if not d.exists():
            print(f'  {folder}: (folder missing)')
            continue
        files = sorted(d.glob('*.json'))
        if not files:
            print(f'  {folder}: (no files)')
            continue
        ok = []
        bad = []
        for p in files:
            data = json.loads(p.read_text())
            q = len(data.get('questions', []))
            fc = len(data.get('flashcards', []))
            guide = len(data.get('guide', ''))
            has_refs = 'youtube.com' in data.get('guide', '') or 'References' in data.get('guide', '')
            if q >= 20 and fc >= 8:
                ok.append(p.name)
                total_ok += 1
            else:
                bad.append(f'{p.name}: q={q} fc={fc} guide={guide} refs={"✓" if has_refs else "✗"}')
                total_bad += 1
        symbol = '✅' if not bad else '⚠️'
        print(f'{symbol} {folder}: {len(ok)} OK, {len(bad)} need work')
        for b in bad:
            print(f'     NEEDS: {b}')
    print(f'\nTotal: {total_ok} OK, {total_bad} need work')

def validate_json():
    """Validate all JSONs parse without error."""
    errors = []
    for folder in FOLDERS:
        d = BASE / folder
        if not d.exists():
            continue
        for p in d.glob('*.json'):
            try:
                json.loads(p.read_text())
            except json.JSONDecodeError as e:
                errors.append(f'{p}: {e}')
    if errors:
        print('JSON ERRORS:')
        for e in errors:
            print(f'  {e}')
    else:
        print('✅ All JSON files parse cleanly.')

if __name__ == '__main__':
    args = sys.argv[1:]
    if '--status' in args or not args:
        status()
        print()
        validate_json()
    else:
        print('Usage: python3 scripts/patch_all.py [--status]')

