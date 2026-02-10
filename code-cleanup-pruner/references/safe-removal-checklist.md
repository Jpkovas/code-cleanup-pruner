# Safe Removal Checklist

Use this checklist before finalizing duplicate/dead-code cleanup.

## Scope Control

1. Confirm each change removes one clear thing: duplicate logic, dead branch, or unused symbol/file.
2. Keep behavioral changes out of cleanup commits unless explicitly requested.
3. Preserve public APIs unless change request explicitly includes breaking changes.

## Evidence for Removal

1. Show at least one concrete signal for each removal:
   - no references/imports
   - static analysis warning
   - duplicate block match
   - unreachable condition proof
2. Record file paths and rationale for significant removals.

## Validation Gate

Run the strongest available commands:

1. Tests (prefer full suite)
2. Lint
3. Build/typecheck
4. Any domain-specific smoke checks

If full validation cannot run, state exactly what was not run and why.

## Regression Guard

1. Re-check exports/public entrypoints after removals.
2. Watch for runtime-only references (dynamic imports, reflection, framework conventions).
3. If uncertain, prefer deprecating + TODO with owner/date instead of deleting immediately.
