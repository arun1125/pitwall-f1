#!/bin/bash
# Ralph - autonomous loop (AFK mode)
# Usage: ./scripts/ralph-loop.sh [max_iterations]
# Default: 5 iterations to keep costs controlled

set -e

MAX=${1:-5}

if [ ! -f PRD.md ]; then
  echo "ERROR: No PRD.md found in current directory"
  exit 1
fi

if [ ! -f progress.txt ]; then
  touch progress.txt
fi

echo "Starting Ralph loop — max $MAX iterations"

for ((i=1; i<=MAX; i++)); do
  echo ""
  echo "=== Ralph iteration $i/$MAX ==="
  echo ""

  result=$(claude -p --permission-mode acceptEdits \
    "@PRD.md @progress.txt \
    1. Read the PRD and progress file. \
    2. Find the next incomplete task and implement it. \
    3. Run any relevant tests. \
    4. Commit your changes with a descriptive message. \
    5. Update progress.txt with what you did. \
    6. If ALL tasks in the PRD are complete, output exactly: <done>ALL_COMPLETE</done> \
    ONLY DO ONE TASK AT A TIME.")

  echo "$result"

  if echo "$result" | grep -q "ALL_COMPLETE"; then
    echo ""
    echo "=== Ralph: All PRD tasks complete after $i iterations ==="
    exit 0
  fi
done

echo ""
echo "=== Ralph: Hit max iterations ($MAX). Check progress.txt for status ==="
