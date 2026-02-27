---
name: coding-agent
description: Delegate coding tasks to Codex, Claude Code, or Pi agents via background sub-agent sessions. Use when: (1) building/creating new features or apps, (2) debugging/fixing bugs, (3) refactoring code, (4) writing tests or docs, or (5) running longer coding work asynchronously while the main chat continues.
---

Delegate coding work to a spawned sub-agent and return concise progress + final results.

## Workflow

1. Clarify the coding objective, constraints, and success criteria.
2. Choose agent/model based on task type and speed/quality needs.
3. Spawn a sub-agent with a concrete task.
4. Let it run in background; do not busy-poll.
5. On completion, summarize results, changed files, tests, and next actions.

## Delegation Template

Use this task template when spawning:

- Goal
- Codebase path
- Required changes
- Acceptance criteria
- Test commands
- Output format (summary + diff highlights)

## Suggested Agent Routing

- Codex: general coding, fast iteration, repo edits/tests.
- Claude Code: architecture-heavy refactors and long-form reasoning.
- Pi: lightweight scripting and quick utility tasks.

## Default Spawn Settings

- mode: `run` for one-off tasks.
- cleanup: `keep` if follow-up likely; otherwise `delete`.
- timeout: set realistic `runTimeoutSeconds` for bigger changes.

## Result Format

Return:

1. What changed
2. Files touched
3. Test/lint results
4. Risks or open questions
5. Next step recommendation

Keep responses concise unless user asks for full detail.
