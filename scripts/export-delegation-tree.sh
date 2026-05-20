#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  python3 "$SCRIPT_DIR/export-delegation-tree.py" "$@"
elif command -v python >/dev/null 2>&1; then
  python "$SCRIPT_DIR/export-delegation-tree.py" "$@"
else
  echo "python3 or python is required to export delegation trees" >&2
  exit 127
fi
