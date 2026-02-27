---
name: github
description: GitHub operations via gh CLI: issues, PRs, CI runs, code review, and API queries. Use when: (1) checking PR status or CI, (2) creating/commenting/updating issues or PRs, (3) reviewing code and posting feedback, (4) querying GitHub metadata via gh api, or (5) triaging repositories and workflows.
---

Use `gh` as the default interface for GitHub tasks.

## Core Workflow

1. Confirm target repo/owner and branch or PR/issue number.
2. Run the relevant `gh` command(s).
3. Return concise, actionable results with links/IDs.
4. For write actions (comments, edits, closes), summarize exactly what changed.

## Common Commands

### PRs

```bash
gh pr status
gh pr view <number> --comments --web
gh pr checks <number>
gh pr comment <number> --body "..."
gh pr create --title "..." --body "..."
```

### Issues

```bash
gh issue list
gh issue view <number>
gh issue comment <number> --body "..."
gh issue create --title "..." --body "..."
gh issue edit <number> --add-label "..."
```

### CI / Actions

```bash
gh run list
gh run view <run-id> --log
gh run rerun <run-id>
gh workflow list
gh workflow run <workflow.yml>
```

### API Queries

```bash
gh api repos/{owner}/{repo}
gh api repos/{owner}/{repo}/pulls/<number>/files
```

## Response Format

Return:

1. Status summary
2. Key findings (failures, blockers, requested changes)
3. Exact actions taken
4. Next recommended action

Keep output short unless the user asks for full logs.
