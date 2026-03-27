#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path('/home/han/.openclaw/workspace/usage')
SNAP_FILE = DATA_DIR / 'openclaw_usage_snapshots.jsonl'
REPORT_FILE = DATA_DIR / 'daily_model_usage.json'


OPENCLAW_BIN = '/home/han/.npm-global/bin/openclaw'


def run_status_json():
    # Use full path so this works in cron/heartbeat contexts where PATH is limited
    candidates = [OPENCLAW_BIN, 'openclaw']
    for cmd in candidates:
        try:
            out = subprocess.check_output([cmd, 'status', '--json'], text=True, stderr=subprocess.DEVNULL)
            return json.loads(out)
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            continue
    print('run_status_json failed: openclaw not found or returned invalid JSON')
    return {}


def capture_snapshot():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = run_status_json()
    now = dt.datetime.now(dt.timezone.utc).isoformat()

    rows = []
    for s in payload.get('sessions', {}).get('recent', []):
        rows.append({
            'capturedAt': now,
            'sessionKey': s.get('key'),
            'model': s.get('model'),
            'inputTokens': s.get('inputTokens') or 0,
            'outputTokens': s.get('outputTokens') or 0,
            'cacheRead': s.get('cacheRead') or 0,
            'cacheWrite': s.get('cacheWrite') or 0,
            'totalTokens': s.get('totalTokens') or 0,
        })

    with SNAP_FILE.open('a', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    print(f'captured {len(rows)} session rows -> {SNAP_FILE}')


def load_rows():
    if not SNAP_FILE.exists():
        return []
    rows = []
    errors = []
    with SNAP_FILE.open('r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                # Log corrupted lines but continue processing
                errors.append(f"Line {line_num}: {e} | Data: {line[:80]}")
                continue
    
    if errors:
        print(f"⚠️  Skipped {len(errors)} corrupted line(s) in {SNAP_FILE}:", file=__import__('sys').stderr)
        for err in errors[:5]:  # Show first 5 errors
            print(f"  {err}", file=__import__('sys').stderr)
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more", file=__import__('sys').stderr)
    
    return rows


def report():
    rows = load_rows()
    if not rows:
        print('no snapshots yet')
        return

    # sort chronologically
    rows.sort(key=lambda r: r['capturedAt'])

    # delta-based aggregation per day/model to avoid double-counting snapshots
    # key for monotonic counters: sessionKey + model
    prev = {}
    agg = defaultdict(lambda: {'inputTokens': 0, 'outputTokens': 0, 'cacheRead': 0, 'cacheWrite': 0})

    for r in rows:
        key = (r['sessionKey'], r['model'])
        day = r['capturedAt'][:10]
        p = prev.get(key)

        if p is None:
            di = r['inputTokens']
            do = r['outputTokens']
            dcr = r['cacheRead']
            dcw = r['cacheWrite']
        else:
            di = max(0, r['inputTokens'] - p['inputTokens'])
            do = max(0, r['outputTokens'] - p['outputTokens'])
            dcr = max(0, r['cacheRead'] - p['cacheRead'])
            dcw = max(0, r['cacheWrite'] - p['cacheWrite'])

        bucket = agg[(day, r['model'])]
        bucket['inputTokens'] += di
        bucket['outputTokens'] += do
        bucket['cacheRead'] += dcr
        bucket['cacheWrite'] += dcw

        prev[key] = r

    out = []
    for (day, model), vals in sorted(agg.items()):
        out.append({'day': day, 'model': model, **vals})

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_FILE.open('w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(out, ensure_ascii=False, indent=2))
    print(f'\nwritten: {REPORT_FILE}')


def main():
    ap = argparse.ArgumentParser(description='Track OpenClaw per-day/per-model token usage')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('capture')
    sub.add_parser('report')
    args = ap.parse_args()

    if args.cmd == 'capture':
        capture_snapshot()
    elif args.cmd == 'report':
        report()


if __name__ == '__main__':
    main()
