---
name: ship
description: >-
  Stage, commit, push, and verify CI passes — the full "get code to remote"
  workflow in one command. Use whenever the user says "ship it", "commit and
  push", "push and check CI", "ship this", "land it", "send it", "commit push
  verify", or any variation of wanting their changes committed, pushed, and
  verified in CI. Also triggers on "check pipeline", "is CI green", "fix CI
  and re-push". Handles the entire loop: stage specific files, write a good
  commit message, push, poll GitHub Actions, and if CI fails, fix lint/test
  issues, re-stage, re-commit, and re-push until green.
---

# Ship — Commit, Push, Verify CI

Full workflow to get local changes safely landed on remote with passing CI.

## Workflow

### 1. Assess changes

```bash
git status
git diff --stat
git diff          # staged + unstaged
git log --oneline -5   # recent commits for message style
```

Review what's changed. Group changes logically — if there are unrelated changes, consider splitting into multiple commits (ask the user if unclear).

### 2. Stage and commit

- Stage specific files by name — avoid `git add -A` or `git add .` to prevent accidentally including secrets (.env, credentials) or large binaries
- If unsure which files belong together, ask
- Write a concise commit message: type(scope): description
  - Types: feat, fix, refactor, docs, test, chore, perf
  - Focus on the "why", not the "what"
  - Use HEREDOC format for the commit message

```bash
git add <specific files>
git commit -m "$(cat <<'EOF'
feat(signals): add vortex trend filter to EMA entry
EOF
)"
```

### 3. Push

```bash
git push
```

If the branch has no upstream, use `git push -u origin <branch>`.

### 4. Verify CI

```bash
gh run list --limit 3
```

Wait a moment for the run to appear, then watch it:

```bash
gh run watch          # watches the most recent run
```

If CI is already done:

```bash
gh run view --log-failed   # show only failed job logs
```

### 5. Fix and retry (if CI fails)

Common failures in this repo:

| Failure | Fix |
|---------|-----|
| ruff lint | `uv run ruff check --fix <files>` then re-stage |
| ruff format | `uv run ruff format <files>` then re-stage |
| pytest | Read the failure, fix the test or code |
| Pine validation | `./scripts/validate-pine.sh Tradingview/*.pine` |
| Go tests | `just test-go` locally first |
| TypeScript | `cd Tradovate && npm run lint` |

After fixing:

```bash
git add <fixed files>
git commit -m "$(cat <<'EOF'
fix: resolve ruff lint errors
EOF
)"
git push
```

Then re-check CI. Repeat until green.

### 6. Confirm

Once CI is green, report the status to the user with a link to the passing run.

## Important rules

- Never commit .env files, credentials, or secrets
- Never use `--no-verify` to skip hooks — fix the underlying issue
- Never amend published commits without explicit permission
- If pre-commit hooks fail, fix the issue and create a NEW commit (don't amend)
- Run `pre-commit run --all-files` locally before pushing if you want to catch issues early
- Ruff auto-fix during pre-commit can leave unstaged changes — always re-stage after hook failure
