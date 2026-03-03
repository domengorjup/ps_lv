#\!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"

jupyter-book build "$SCRIPT_DIR/lv_book" || { echo "jupyter-book build failed"; return 1 2>/dev/null; exit 1; }
ghp-import -n -p -f -r ssh "$SCRIPT_DIR/lv_book/_build/html" || { echo "ghp-import failed"; return 1 2>/dev/null; exit 1; }
