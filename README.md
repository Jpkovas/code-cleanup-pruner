# code-cleanup-pruner skill

Repository ready for installation with `npx skills`.

## Structure

- `code-cleanup-pruner/SKILL.md`
- `code-cleanup-pruner/agents/openai.yaml`
- `code-cleanup-pruner/scripts/find_duplicate_blocks.py`
- `code-cleanup-pruner/references/safe-removal-checklist.md`

## Installation via npx skills

After publishing this repository to GitHub:

```bash
npx skills add Jpkovas/code-cleanup-pruner
```

To install directly without an interactive prompt:

```bash
npx skills add Jpkovas/code-cleanup-pruner --skill code-cleanup-pruner -y
```

## Quick verification

List skills available in the repository:

```bash
npx skills add Jpkovas/code-cleanup-pruner --list
```
