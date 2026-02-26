#!/bin/bash
# Ralph - single iteration (human-in-the-loop)
# Run from project root. Reviews PRD + progress, does ONE task, commits.

set -e

if [ ! -f PRD.md ]; then
  echo "ERROR: No PRD.md found in current directory"
  exit 1
fi

if [ ! -f progress.txt ]; then
  touch progress.txt
fi

claude --permission-mode acceptEdits \
  "@PRD.md @progress.txt \
  1. Read the PRD and progress file. \
  2. Find the next incomplete task and implement it. \
  3. Run any relevant tests. \
  4. Commit your changes with a descriptive message. \
  5. Update progress.txt with what you did. \
  ONLY DO ONE TASK AT A TIME."
