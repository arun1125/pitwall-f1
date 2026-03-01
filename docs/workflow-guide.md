# Agentic Dev Workflow

Build apps using structured planning and autonomous execution.

## The Pipeline

```
/kickoff → /feature → /write-a-prd → /prd-to-issues → ralph-loop.sh → QA
```

## Two Commands

### `/kickoff` — Start a new project (run once)

Opens Claude Code and sets up everything:

1. Interviews you about your stack, constraints, and design rules
2. Writes a CLAUDE.md tailored to your project
3. Creates a GitHub repo and pushes initial commit
4. Creates a GitHub Projects board (Todo → In Progress → Done)
5. Installs all skills and ralph scripts

After kickoff, your project has:
```
my-app/
├── CLAUDE.md                      # Project context for Claude
├── progress.txt                   # Ralph's handoff log between iterations
├── scripts/
│   ├── ralph-once.sh              # Single task, human reviews after
│   └── ralph-loop.sh              # N tasks autonomously
└── .claude/skills/
    ├── write-a-prd/               # Feature planning interview → PRD
    ├── prd-to-issues/             # PRD → vertical-slice GitHub issues
    ├── tdd/                       # Test-driven development
    ├── kickoff/                   # This setup command
    └── feature/                   # The feature-building pipeline
```

### `/feature` — Add a feature (run every time)

Runs the full build pipeline:

1. **Plan** — `/write-a-prd` interviews you about the feature, explores the codebase, and creates a PRD as a GitHub issue
2. **Break down** — `/prd-to-issues` splits the PRD into vertical-slice issues with dependencies, adds them to the GitHub board
3. **Build** — You run `./scripts/ralph-loop.sh N` in a separate terminal. Ralph works through issues one at a time.
4. **QA** — You review what ralph built, fix anything broken

## How Ralph Works

Ralph is a bash script that spawns fresh Claude Code sessions in a loop.

```bash
./scripts/ralph-loop.sh 4    # Run from a separate terminal (not inside Claude Code)
```

Each iteration:
1. Spawns a headless `claude -p` session
2. Reads open GitHub issues via `gh issue list`
3. Reads `progress.txt` to see what prior iterations did
4. Picks the lowest-numbered unblocked issue
5. Implements it fully (code + tests)
6. Runs tests, commits with `Closes #N`, pushes
7. Appends to `progress.txt` as a handoff to the next iteration
8. Exits — next iteration starts fresh

**Why fresh sessions?** Each issue gets a clean context window. No accumulated state, no confusion. `progress.txt` is the handoff mechanism.

**Two modes:**
- `ralph-once.sh` — Interactive. Does one issue, you review, then run again.
- `ralph-loop.sh N` — Autonomous. Does up to N issues back-to-back. Stops early if all issues are done.

**Important:** Ralph can't run inside Claude Code. Always run it from a plain terminal.

## GitHub Projects Board

Issues created by `/prd-to-issues` land on the board automatically. The board has three columns:

| Todo | In Progress | Done |
|------|-------------|------|

View it at: `https://github.com/users/<username>/projects/<number>`

Or via CLI:
```bash
gh project list --owner <username>
gh project item-list <number> --owner <username>
```

Issues close automatically when ralph pushes commits with `Closes #N`.

## Vertical Slices

`/prd-to-issues` breaks features into **tracer bullets**, not horizontal layers. Each issue is a thin end-to-end slice:

```
Bad (horizontal):                Good (vertical):
─────────────────                ─────────────────
Issue 1: All API endpoints       Issue 1: Year/race selector + API
Issue 2: All frontend             Issue 2: Lap chart + API
Issue 3: All tests                Issue 3: Stats panel
                                  Issue 4: E2E tests
```

Each slice is independently demoable. Ralph can build and test each one without needing the others to be complete.

Issues include:
- **Blocked by** — which issues must finish first
- **Acceptance criteria** — checkboxes ralph uses to verify completion
- **User stories** — traced back to the PRD

## Example: Full Run

```bash
# 1. Scaffold
~/Desktop/00_Organized/Agents/tech/scripts/init-project.sh my-dashboard
cd my-dashboard

# 2. Start Claude Code
claude

# 3. Set up the project
/kickoff
# → Writes CLAUDE.md, creates GitHub repo + board

# 4. Build first feature
/feature
# → Interviews you about the feature
# → Creates PRD issue (#1)
# → Creates 4 implementation issues (#2-#5) on the board

# 5. In a SEPARATE terminal:
./scripts/ralph-loop.sh 4
# → Builds issues #2, #3, #4, #5 autonomously
# → Each issue: implement → test → commit → push → close

# 6. Back in Claude Code:
# → Start the server, QA the feature
# → Run /feature again for the next one
```

## Prerequisites

- **Claude Code** (`claude` CLI)
- **GitHub CLI** (`brew install gh && gh auth login`)
  - Needs project scopes: `gh auth refresh -h github.com -s project,read:project`
- **Git** configured with SSH access to GitHub

## Files Reference

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project context — stack, rules, DB schema. Read by every Claude session. |
| `progress.txt` | Ralph's log. Each iteration appends what it did. Handoff between sessions. |
| `scripts/ralph-once.sh` | Run one issue with human review after. |
| `scripts/ralph-loop.sh` | Run N issues autonomously. |
| `.claude/skills/write-a-prd/` | Feature planning interview → structured PRD. |
| `.claude/skills/prd-to-issues/` | PRD → vertical-slice GitHub issues. |
| `.claude/skills/tdd/` | Test-driven development loop. |
| `.claude/skills/kickoff/` | One-time project setup. |
| `.claude/skills/feature/` | Full feature pipeline orchestrator. |
