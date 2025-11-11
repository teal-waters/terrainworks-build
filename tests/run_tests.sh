#!/usr/bin/env bash
# set -euo pipefail

# Commands run relative to the directory this file is run.
# So fortran tools need paths to be relative to the same place.

COMMANDS=(
  "MakeGrids/barebones_test.sh"
)

fail=0

for cmd in "${COMMANDS[@]}"; do
  echo -n "$cmd ... "
  output=$(bash "$cmd" 2>&1) || {
    echo "❌ FAIL"
    echo "$output"
    fail=1
    continue
  }

  echo "✅ OK"
done

exit $fail
