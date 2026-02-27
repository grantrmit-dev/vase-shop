# HEARTBEAT.md

On every heartbeat:

1) Review current mistakes/issues and propose concrete fixes or improvements.
2) For this review work, spawn multiple sub-agents and run tasks in parallel.
3) Capture usage snapshot by running:
   `python3 /home/han/.openclaw/workspace/scripts/usage_tracker.py capture`
4) Optionally regenerate report:
   `python3 /home/han/.openclaw/workspace/scripts/usage_tracker.py report`
5) Return a concise summary of findings, recommended actions, and what was delegated.
6) If nothing actionable is found, reply: HEARTBEAT_OK
