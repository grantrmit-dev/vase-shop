#!/usr/bin/env python3
import argparse
import datetime as dt
import fcntl
import json
import os
import subprocess
import sys
import tempfile
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

DATA_DIR = Path('/home/han/.openclaw/workspace/usage')
SNAP_FILE = DATA_DIR / 'openclaw_usage_snapshots.jsonl'
REPORT_FILE = DATA_DIR / 'daily_model_usage.json'
LOCK_FILE = DATA_DIR / '.usage_tracker.lock'
LATEST_FILE = DATA_DIR / 'latest_by_session.json'
MAX_SNAPSHOT_DAYS = 90
COUNTER_FIELDS = ('inputTokens', 'outputTokens', 'cacheRead', 'cacheWrite', 'totalTokens')
RESET_WARNING_THRESHOLD = 25
HEARTBEAT_STATE_FILE = Path('/home/han/.openclaw/workspace/memory/heartbeat-state.json')

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


def _snapshot_row(now, session):
    return {
        'capturedAt': now,
        'sessionId': session.get('sessionId'),
        'sessionKey': session.get('key'),
        'model': session.get('model'),
        'inputTokens': session.get('inputTokens') or 0,
        'outputTokens': session.get('outputTokens') or 0,
        'cacheRead': session.get('cacheRead') or 0,
        'cacheWrite': session.get('cacheWrite') or 0,
        'totalTokens': session.get('totalTokens') or 0,
    }


def _has_any_usage(row):
    return any((row.get(field) or 0) > 0 for field in COUNTER_FIELDS)


def _parse_iso_utc(ts):
    if not ts:
        return None
    try:
        return dt.datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except ValueError:
        return None


@contextmanager
def _tracker_lock():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOCK_FILE.open('a+', encoding='utf-8') as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _atomic_write_lines(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', delete=False, dir=path.parent, encoding='utf-8') as tmp:
        tmp_path = Path(tmp.name)
        for row in rows:
            tmp.write(json.dumps(row, ensure_ascii=False) + '\n')
    os.replace(tmp_path, path)


def _atomic_write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', delete=False, dir=path.parent, encoding='utf-8') as tmp:
        tmp_path = Path(tmp.name)
        json.dump(payload, tmp, ensure_ascii=False, indent=2)
        tmp.write('\n')
    os.replace(tmp_path, path)


def _prune_snapshot_rows(rows):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=MAX_SNAPSHOT_DAYS)
    kept = []
    pruned = 0
    for row in rows:
        captured = _parse_iso_utc(row.get('capturedAt'))
        if captured is None or captured >= cutoff:
            kept.append(row)
        else:
            pruned += 1
    return kept, pruned


def _row_key(row):
    session_id = row.get('sessionId')
    if session_id:
        return f"{session_id}||{row.get('model')}"
    return f"{row.get('sessionKey')}||{row.get('model')}"


def _load_latest_index():
    if not LATEST_FILE.exists():
        return {}
    try:
        return json.loads(LATEST_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}


def _counters_unchanged(previous, current):
    return all((previous.get(field) or 0) == (current.get(field) or 0) for field in COUNTER_FIELDS)


def _update_heartbeat_state(statuses, mark_workspace_review=True):
    now = dt.datetime.now(dt.timezone.utc)

    existing = {}
    if HEARTBEAT_STATE_FILE.exists():
        try:
            existing = json.loads(HEARTBEAT_STATE_FILE.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            existing = {}

    payload = {
        'lastChecks': dict(existing.get('lastChecks') or {}),
        'lastChecksIso': dict(existing.get('lastChecksIso') or {}),
        'lastHeartbeatSummary': dict(existing.get('lastHeartbeatSummary') or {}),
    }

    if mark_workspace_review:
        payload['lastChecks']['workspace_review'] = int(now.timestamp())
        payload['lastChecksIso']['workspace_review'] = now.isoformat()

    payload['lastHeartbeatSummary'].update(statuses)

    summary = payload['lastHeartbeatSummary']
    if summary.get('workspace_review') == 'completed' and mark_workspace_review:
        payload['lastChecks']['workspace_review'] = int(now.timestamp())
        payload['lastChecksIso']['workspace_review'] = now.isoformat()
    elif summary.get('workspace_review') in {'pending-review', 'failed', 'skipped'} and not mark_workspace_review:
        payload['lastChecks']['workspace_review'] = payload['lastChecks'].get('workspace_review')
        payload['lastChecksIso']['workspace_review'] = payload['lastChecksIso'].get('workspace_review')

    _atomic_write_json(HEARTBEAT_STATE_FILE, payload)


def capture_snapshot():
    payload = run_status_json()
    now = dt.datetime.now(dt.timezone.utc).isoformat()

    rows = []
    skipped_zero = 0
    skipped_unchanged = 0

    with _tracker_lock():
        existing_rows = load_rows(log_errors=False)
        latest_index = _load_latest_index()

        for s in payload.get('sessions', {}).get('recent', []):
            row = _snapshot_row(now, s)
            if not _has_any_usage(row):
                skipped_zero += 1
                continue

            key = _row_key(row)
            previous = latest_index.get(key)
            if previous and _counters_unchanged(previous, row):
                skipped_unchanged += 1
                continue

            rows.append(row)
            latest_index[key] = row

        combined_rows = existing_rows + rows
        kept_rows, pruned = _prune_snapshot_rows(combined_rows)
        _atomic_write_lines(SNAP_FILE, kept_rows)
        _atomic_write_json(LATEST_FILE, latest_index)

    _update_heartbeat_state({
        'capture': 'completed',
        'report': 'not-run-yet',
        'workspace_review': 'pending-review',
    }, mark_workspace_review=False)

    print(
        f'captured {len(rows)} session rows -> {SNAP_FILE}'
        f' (skipped {skipped_zero} zero-usage, skipped {skipped_unchanged} unchanged, pruned {pruned} old rows)'
    )


def load_rows(log_errors=True):
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
                errors.append(f"Line {line_num}: {e} | Data: {line[:80]}")
                continue

    if errors and log_errors:
        print(f"⚠️  Skipped {len(errors)} corrupted line(s) in {SNAP_FILE}:", file=sys.stderr)
        for err in errors[:5]:
            print(f"  {err}", file=sys.stderr)
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more", file=sys.stderr)

    return rows


def _has_counter_reset(previous, current):
    return any((current.get(field) or 0) < (previous.get(field) or 0) for field in COUNTER_FIELDS)


def _compute_delta(previous, current):
    if previous is None or _has_counter_reset(previous, current):
        return {field: current.get(field) or 0 for field in COUNTER_FIELDS}, previous is not None

    return {
        field: max(0, (current.get(field) or 0) - (previous.get(field) or 0))
        for field in COUNTER_FIELDS
    }, False


def report():
    with _tracker_lock():
        rows = load_rows()
        if not rows:
            print('no snapshots yet')
            return

        rows = [row for row in rows if _has_any_usage(row)]
        if not rows:
            print('no non-zero snapshots yet')
            return

        rows.sort(key=lambda r: r.get('capturedAt', ''))

        prev = {}
        agg = defaultdict(lambda: {'inputTokens': 0, 'outputTokens': 0, 'cacheRead': 0, 'cacheWrite': 0})
        resets_detected = 0
        reset_keys = set()

        for r in rows:
            key = (_row_key(r), r.get('model'))
            day = (r.get('capturedAt') or '')[:10]
            if not day:
                continue

            delta, reset_detected = _compute_delta(prev.get(key), r)
            if reset_detected and key not in reset_keys:
                resets_detected += 1
                reset_keys.add(key)

            if any(delta[field] > 0 for field in ('inputTokens', 'outputTokens', 'cacheRead', 'cacheWrite')):
                bucket = agg[(day, r.get('model'))]
                bucket['inputTokens'] += delta['inputTokens']
                bucket['outputTokens'] += delta['outputTokens']
                bucket['cacheRead'] += delta['cacheRead']
                bucket['cacheWrite'] += delta['cacheWrite']

            prev[key] = r

        out = []
        for (day, model), vals in sorted(agg.items()):
            out.append({
                'day': day,
                'model': model,
                **vals,
                'note': 'Usage is bucketed by snapshot day; cross-midnight attribution remains approximate.'
            })

        _atomic_write_json(REPORT_FILE, out)

    _update_heartbeat_state({
        'workspace_review': 'completed',
        'capture': 'completed',
        'report': 'completed',
    }, mark_workspace_review=True)

    print(json.dumps(out, ensure_ascii=False, indent=2))
    print(f'\nwritten: {REPORT_FILE}')
    if resets_detected:
        print(f'detected {resets_detected} counter reset(s); treated as new baselines')
    if resets_detected > RESET_WARNING_THRESHOLD:
        print(
            f'warning: reset count {resets_detected} exceeds threshold {RESET_WARNING_THRESHOLD}; '
            'totals may still be distorted by reused session identities or frequent restarts',
            file=sys.stderr,
        )


def compact_snapshots():
    with _tracker_lock():
        rows = load_rows()
        if not rows:
            print('no snapshots yet')
            return

        rows.sort(key=lambda r: r.get('capturedAt', ''))
        compacted = []
        prev_by_key = {}
        removed = 0

        for row in rows:
            key = _row_key(row)
            previous = prev_by_key.get(key)
            if previous and _counters_unchanged(previous, row):
                removed += 1
                continue
            compacted.append(row)
            prev_by_key[key] = row

        compacted, pruned = _prune_snapshot_rows(compacted)
        latest_index = { _row_key(row): row for row in compacted if _has_any_usage(row) }
        _atomic_write_lines(SNAP_FILE, compacted)
        _atomic_write_json(LATEST_FILE, latest_index)

    print(
        f'compacted snapshots -> kept {len(compacted)} rows, removed {removed} unchanged rows, pruned {pruned} old rows'
    )


def main():
    ap = argparse.ArgumentParser(description='Track OpenClaw per-day/per-model token usage')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('capture')
    sub.add_parser('report')
    sub.add_parser('compact')
    args = ap.parse_args()

    if args.cmd == 'capture':
        capture_snapshot()
    elif args.cmd == 'report':
        report()
    elif args.cmd == 'compact':
        compact_snapshots()


if __name__ == '__main__':
    main()
