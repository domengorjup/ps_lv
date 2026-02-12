#\!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"

jupyter-book build "$SCRIPT_DIR/lv_book" || { echo "jupyter-book build failed"; exit 1; }
ghp-import -n -p -f -r ssh "$SCRIPT_DIR/lv_book/_build/html" || { echo "ghp-import failed"; exit 1; }
