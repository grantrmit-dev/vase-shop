# HEARTBEAT.md

On every heartbeat:

1) Review current mistakes/issues and propose concrete fixes or improvements.
2) For this review work, spawn multiple sub-agents and run tasks in parallel.
3) Capture usage snapshot by running:
   `python3 /home/han/.openclaw/workspace/scripts/usage_tracker.py capture`
4) Regenerate usage report by running:
   `python3 /home/han/.openclaw/workspace/scripts/usage_tracker.py report`
5) Return a concise summary of findings, recommended actions, and what was delegated.
6) If nothing actionable is found, reply: HEARTBEAT_OK

## Execution rules

- Treat steps 3 (`capture`) and 4 (`report`) as required, not optional.
- If any required step is skipped or fails, say so explicitly in the reply.
- Use parallel sub-agents for review work, but keep the scope bounded.
- Fast-path fallback: if delegated review is delayed or fails, return partial findings from local review instead of hanging.
- Prefer one acknowledgement and one final summary; avoid drip-feeding status unless something materially changes.
- After any claimed model switch, verify the actual runtime/model before reporting it to Han.
