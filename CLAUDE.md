# Helen Workflow Test

Test environment for Matt Pocock's agentic workflow: skills + ralph loop.

## Stack

This is a test app. Keep it simple — vanilla HTML/CSS/JS or a minimal framework.
No complex build tools. The point is testing the workflow, not the tech.

## Installed Skills

- `/write-a-prd` — Interview about a feature idea → structured PRD → GitHub issue
- `/prd-to-issues` — Break PRD into vertical-slice GitHub issues with dependencies
- `/tdd` — Test-driven development with red-green-refactor loop

## Ralph Scripts

- `scripts/ralph-once.sh` — Single iteration, human reviews after each step
- `scripts/ralph-loop.sh` — Autonomous loop, caps at N iterations (default 5)

Both read `PRD.md` + `progress.txt` from project root.

## Workflow

1. Start session, describe your feature idea
2. Run `/write-a-prd` — Claude interviews you, outputs PRD.md
3. Run `/prd-to-issues` — breaks PRD into implementation slices
4. Run `./scripts/ralph-once.sh` to execute one task at a time (or ralph-loop.sh for AFK)
5. Review commits, run manual QA
