---
name: fix-lint
description: >-
  Fix lint errors and re-stage files after pre-commit hook failures. Use when
  the user says "fix lint", "fix ruff", "pre-commit failed", "lint errors",
  "fix formatting", "ruff errors", "hook failed", "re-stage", "fix and
  re-stage", or when a commit attempt fails due to pre-commit hooks. Handles
  the full cycle: run pre-commit, apply auto-fixes, re-stage changed files,
  and verify clean. Also use proactively before committing to catch issues
  early.
---

# Fix Lint — Pre-commit Fix and Re-stage

Handle the recurring "pre-commit failed, fix, re-stage" cycle.

## Workflow

### 1. Run pre-commit

```bash
pre-commit run --all-files
```

If it passes, you're done — tell the user and move on.

### 2. Identify failures

Common hook failures in this repo:

| Hook | Auto-fixable? | Fix command |
|------|--------------|-------------|
| ruff (lint) | Yes | `uv run ruff check --fix <files>` |
| ruff (format) | Yes | `uv run ruff format <files>` |
| trailing-whitespace | Yes (auto-fixed by hook) | Already fixed, just re-stage |
| end-of-file-fixer | Yes (auto-fixed by hook) | Already fixed, just re-stage |
| check-yaml | No | Manual fix |
| check-json | No | Manual fix |
| Pine validation | No | Fix the .pine file manually |
| eslint | Partial | `npm run lint -- --fix` |
| go vet | No | Fix the Go code |
| dotnet build | No | Fix the C# code |

### 3. Apply auto-fixes

For ruff issues (the most common):

```bash
uv run ruff check --fix .
uv run ruff format .
```

For hooks that auto-fix (trailing whitespace, end-of-file), the hook already modified the files — just re-stage them.

### 4. Re-stage fixed files

This is the critical step that people forget. Ruff auto-fix modifies files but doesn't stage them, so the commit will fail again if you don't re-stage:

```bash
git add <files that were modified by auto-fix>
```

Check which files were modified:

```bash
git diff --name-only   # unstaged changes = files modified by auto-fix
```

### 5. Verify clean

```bash
pre-commit run --all-files
```

If still failing, read the error output carefully and fix manually.

### 6. Report

Tell the user what was fixed and that files are re-staged and ready to commit.

## Important

- Never use `--no-verify` to skip hooks — always fix the underlying issue
- Ruff auto-fix during pre-commit leaves unstaged changes — ALWAYS check `git diff --name-only` after a hook failure and re-stage
- If a hook modifies a file you didn't change, include it in the commit anyway (it's a legitimate fix)
- This repo has ~20 pre-commit hooks across Python, Go, C#, Pine Script, and JavaScript — not all are auto-fixable
