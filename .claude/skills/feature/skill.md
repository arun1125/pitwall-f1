# /feature — Add a feature

Use when the user wants to plan and build a new feature. This runs the full pipeline:

```
Idea → /write-a-prd → PRD Issue → /prd-to-issues → GitHub Board → ralph-loop.sh → QA
```

## Process

### Step 1: Plan the feature

Run the `/write-a-prd` skill. This interviews the user about the feature, explores the codebase, and outputs a structured PRD.

The PRD is created as a GitHub issue.

### Step 2: Break into issues

Run the `/prd-to-issues` skill. This takes the PRD issue and breaks it into vertical-slice implementation issues with dependency mapping.

Each issue is added to the GitHub Projects board.

### Step 3: Hand off to ralph

After all issues are created and on the board, tell the user:

```
Issues are on the board. To build them, open a separate terminal and run:

  ./scripts/ralph-loop.sh <N>

where N = number of issues created.

Ralph will work through them in order, one per iteration.
When it's done, come back here for QA.
```

### Step 4: QA

After ralph finishes, help the user:
1. Start the dev server
2. Walk through each issue's acceptance criteria
3. Fix anything that's broken

## Rules

- Always create the PRD as a GitHub issue first
- Always add implementation issues to the GitHub Projects board
- Never skip the interview step — the PRD quality determines build quality
- If the project doesn't have a GitHub repo or board yet, tell the user to run `/kickoff` first
