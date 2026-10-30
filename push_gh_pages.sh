#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"
cd "$SCRIPT_DIR" || exit 1

fail() { echo "$1"; exit 1; }

echo "Reminder: Slovenian notebooks are the source. If you edited them, port the change to notebooks/en/ before deploying."
if ! python tools/check_translation_sync.py; then
    read -r -p "Translation drift reported above. Continue anyway? (y/N) " answer
    [ "$answer" = "y" ] || fail "Aborted."
fi

"$SCRIPT_DIR/build_book.sh" || fail "build failed"

ghp-import -n -p -f -r ssh _site || fail "ghp-import failed"
