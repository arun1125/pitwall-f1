# /kickoff — Start a new project

Use when the user wants to start a new project from scratch or set up the agentic workflow in an existing project.

## What it does

Sets up everything needed so `/feature` and `ralph-loop.sh` work:

1. **CLAUDE.md** — Interview the user about their stack, database, design rules, and constraints. Write a CLAUDE.md tailored to their project.
2. **Git + GitHub** — Initialize git (if needed), create a GitHub repo (`gh repo create`), push initial commit.
3. **GitHub Projects board** — Create a project board (`gh project create`) and link the repo.
4. **Skills** — Copy `/write-a-prd`, `/prd-to-issues`, `/tdd`, `/kickoff`, and `/feature` into `.claude/skills/`.
5. **Ralph scripts** — Create `scripts/ralph-once.sh` and `scripts/ralph-loop.sh`.
6. **progress.txt** — Create empty progress file.

## Interview questions

Ask the user:
- What are you building? (one sentence)
- What's the tech stack? (backend, frontend, database, etc.)
- Any design constraints? (theme, mobile-first, accessibility)
- Is the database pre-built or will you create it?
- Any rules? (no ORM, read-only DB, specific test framework, etc.)

Use their answers to write the CLAUDE.md.

## Ralph scripts

`ralph-once.sh`:
```bash
#!/bin/bash
set -e
[ ! -f progress.txt ] && touch progress.txt
claude --dangerously-skip-permissions \
  "@CLAUDE.md @progress.txt \
  You are Ralph, an autonomous coding agent. \
  1. Run 'gh issue list -s open --json number,title,body -L 20' to find open issues. \
  2. Read progress.txt to see what's been done already. \
  3. Pick the LOWEST numbered non-PRD issue that is not blocked. \
  4. Implement the issue fully — code, tests, everything in the acceptance criteria. \
  5. Run relevant tests and ensure they pass. \
  6. Commit with 'Closes #N' in the message. \
  7. Push to origin. \
  8. Update progress.txt (append). \
  ONLY DO ONE ISSUE AT A TIME."
```

`ralph-loop.sh`:
```bash
#!/bin/bash
set -e
MAX=${1:-5}
[ ! -f progress.txt ] && touch progress.txt
echo "Starting Ralph loop — max $MAX iterations"
for ((i=1; i<=MAX; i++)); do
  echo ""
  echo "=== Ralph iteration $i/$MAX ==="
  echo ""
  result=$(claude -p --dangerously-skip-permissions \
    "@CLAUDE.md @progress.txt \
    You are Ralph, an autonomous coding agent. \
    1. Run 'gh issue list -s open --json number,title,body -L 20' to find open issues. \
    2. Read progress.txt to see what's been done already. \
    3. Pick the LOWEST numbered non-PRD issue that is not blocked. \
    4. Implement the issue fully — code, tests, everything in the acceptance criteria. \
    5. Run relevant tests and ensure they pass. \
    6. Commit with 'Closes #N' in the message. \
    7. Push to origin. \
    8. Update progress.txt (append). \
    9. If NO open non-PRD issues remain, output: <done>ALL_COMPLETE</done> \
    ONLY DO ONE ISSUE AT A TIME.")
  echo "$result"
  if echo "$result" | grep -q "ALL_COMPLETE"; then
    echo ""
    echo "=== Ralph: All issues complete after $i iterations ==="
    exit 0
  fi
done
echo ""
echo "=== Ralph: Hit max iterations ($MAX). Check progress.txt ==="
```

## Checklist

After running, confirm:
- [ ] CLAUDE.md exists with project context
- [ ] GitHub repo created and pushed
- [ ] Projects board created and linked
- [ ] `.claude/skills/` has all 5 skills
- [ ] `scripts/ralph-once.sh` and `scripts/ralph-loop.sh` exist and are executable
- [ ] `progress.txt` exists
- [ ] Tell the user: "Run `/feature` to plan and build your first feature."
