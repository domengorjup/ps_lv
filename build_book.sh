#!/usr/bin/env bash
# Build both language versions and assemble the site in _site/ (sl at root, en under en/).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"
cd "$SCRIPT_DIR" || exit 1

fail() { echo "$1"; exit 1; }

# jupyter-book always appends _build/ to --path-output, hence _build/sl/_build/html.
rm -rf lv_book/_build/sl/_build/html lv_book/_build/en/_build/html
jupyter-book build lv_book --path-output lv_book/_build/sl || fail "jupyter-book build (sl) failed"
jupyter-book build lv_book --config "$SCRIPT_DIR/lv_book/_config.en.yml" --toc "$SCRIPT_DIR/lv_book/_toc.en.yml" --path-output lv_book/_build/en || fail "jupyter-book build (en) failed"

rm -rf _site
mkdir -p _site/en
cp -r lv_book/_build/sl/_build/html/. _site/ || fail "copy of sl html failed"
cp -r lv_book/_build/en/_build/html/. _site/en/ || fail "copy of en html failed"
touch _site/.nojekyll

echo
echo "Site assembled in _site/. Open locally:"
echo "  file://$SCRIPT_DIR/_site/index.html"
echo "  file://$SCRIPT_DIR/_site/en/index.html"
