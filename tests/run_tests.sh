#!/usr/bin/env bash
# set -euo pipefail

# Commands run relative to the directory this file is run.
# So fortran tools need paths to be relative to the same place.

COMMANDS=(
  "MakeGrids/barebones_test.sh"
)

for cmd in "${COMMANDS[@]}"; do
  echo -n "$cmd ... "
  if eval "source $cmd" > /dev/null 2>&1; then
    echo "✅ OK"
  else
    echo "❌ FAIL"
  fi
done
