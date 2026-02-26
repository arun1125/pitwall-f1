#!/bin/bash
# Ralph - autonomous loop (AFK mode)
# Usage: ./scripts/ralph-loop.sh [max_iterations]
# Default: 5 iterations to keep costs controlled

set -e

MAX=${1:-5}

if [ ! -f progress.txt ]; then
  touch progress.txt
fi

echo "Starting Ralph loop — max $MAX iterations"

for ((i=1; i<=MAX; i++)); do
  echo ""
  echo "=== Ralph iteration $i/$MAX ==="
  echo ""

  result=$(claude -p --permission-mode acceptEdits \
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
    9. If there are NO open non-PRD issues left, output exactly: <done>ALL_COMPLETE</done> \
    ONLY DO ONE ISSUE AT A TIME. Do not modify the database.")

  echo "$result"

  if echo "$result" | grep -q "ALL_COMPLETE"; then
    echo ""
    echo "=== Ralph: All issues complete after $i iterations ==="
    exit 0
  fi
done

echo ""
echo "=== Ralph: Hit max iterations ($MAX). Check progress.txt for status ==="
