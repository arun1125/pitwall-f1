#!/bin/bash
# Ralph - single iteration (human-in-the-loop)
# Run from project root. Reads GitHub issues, does ONE task, commits.

set -e

if [ ! -f progress.txt ]; then
  touch progress.txt
fi

claude --permission-mode acceptEdits \
  "@CLAUDE.md @progress.txt \
  You are Ralph, an autonomous coding agent. \
  1. Run 'gh issue list -s open --json number,title,body -L 20' to find open issues. \
  2. Read progress.txt to see what's been done already. \
  3. Pick the LOWEST numbered non-PRD issue that is not blocked (check the 'Blocked by' section in the issue body — if the blocking issue is still open, skip it). \
  4. Implement the issue fully — code, tests, everything in the acceptance criteria. \
  5. Run all tests with 'python -m pytest tests/ -v' and ensure they pass. \
  6. Commit your changes with a descriptive message that includes 'Closes #N'. \
  7. Push to origin. \
  8. Update progress.txt with what you did (append, don't overwrite). \
  ONLY DO ONE ISSUE AT A TIME. Do not modify the database."
