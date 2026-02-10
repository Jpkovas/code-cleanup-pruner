---
name: code-cleanup-pruner
description: Remove duplicate and dead code safely while preserving behavior. Use when Codex is asked to clean "code trash", eliminate repeated logic, remove unused modules/functions/files, simplify legacy branches, or reduce technical debt with test-backed changes.
---

# Code Cleanup Pruner

## Overview

Follow a behavior-preserving cleanup workflow: detect candidates, remove only what is defensible, and prove no regressions with lint/build/tests before finishing.

## Workflow

### 1) Build a Safe Baseline

1. Inspect current repo state with `git status --short`.
2. Identify validation commands used by the project (`test`, `lint`, `build`, static analysis).
3. Run at least one relevant validation command before editing to establish a baseline.

### 2) Find Cleanup Candidates

Use multiple signals instead of guessing:

1. Run `scripts/find_duplicate_blocks.py . --min-lines 10` to detect repeated code blocks.
2. Search for stale markers:
   - `rg -n "TODO.*remove|deprecated|obsolete|legacy|unused|dead code" .`
3. Use language-specific unused checks when available:
   - TypeScript: `npx tsc --noEmit --noUnusedLocals --noUnusedParameters`
   - Python: `ruff check . --select F401,F841`
   - Go: `go vet ./...` (and `staticcheck ./...` when installed)
4. Detect likely orphan files by checking whether modules are imported/referenced.

### 3) Prioritize Low-Risk Removals

Prioritize in this order:

1. Unreferenced private helpers and files.
2. Exact duplicate logic that can be centralized.
3. Conditional branches that are permanently unreachable.

Avoid risky removals unless explicitly requested:

1. Public API surface changes.
2. Behavior changes mixed with cleanup.
3. Large refactors without test coverage.

### 4) Apply Minimal, Traceable Changes

1. Keep each cleanup slice focused on one concern.
2. Preserve observable behavior; if behavior must change, isolate and document it.
3. Document important removals with file paths and rationale.

### 5) Validate Before Delivery

1. Run the strongest available checks (prefer full test suite, lint, and build).
2. If full suite is unavailable, run the broadest subset and state the limitation.
3. Confirm no accidental API/export removals.
4. Use `references/safe-removal-checklist.md` as the final gate.

## Resources

1. `scripts/find_duplicate_blocks.py`: reports repeated normalized code windows to triage dedup opportunities.
2. `references/safe-removal-checklist.md`: final validation checklist for dead-code/duplication cleanup.
