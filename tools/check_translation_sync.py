#!/usr/bin/env python
"""Check that English notebooks/pages mirror the Slovenian sources.

Pairs lv_book/notebooks/sl/NN - *.ipynb with lv_book/notebooks/en/NN - *.ipynb and
compares markdown-cell count, code-cell count and normalised code (comments removed,
string contents replaced by a placeholder). Also warns if intro.md / about.md were
committed more recently than intro_en.md / about_en.md.

Exit code 0: everything OK. 1: drift or missing counterpart.
"""
import io
import re
import subprocess
import sys
import tokenize
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "lv_book"
SL_DIR = BOOK / "notebooks" / "sl"
EN_DIR = BOOK / "notebooks" / "en"
PAGES = [("intro.md", "intro_en.md"), ("about.md", "about_en.md")]
PREFIX = re.compile(r"^(\d\d) - ")


def normalise(source):
    """Remove comments and blank lines, replace string contents by a placeholder."""
    try:
        out = []
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING:
                # keep prefix (r, f, b, ...) and quote type, drop the content
                m = re.match(r"^([A-Za-z]*)('''|\"\"\"|'|\")", tok.string)
                out.append(f"{m.group(1)}{m.group(2)}S{m.group(2)}" if m else "'S'")
                continue
            if hasattr(tokenize, "FSTRING_START") and tok.type in (
                getattr(tokenize, "FSTRING_MIDDLE", -1),
            ):
                out.append("S")
                continue
            out.append(tok.string if tok.type not in (tokenize.NL, tokenize.NEWLINE) else "\n")
        text = "".join(out)  # token text only; spacing is irrelevant for the comparison
    except (tokenize.TokenError, IndentationError, SyntaxError):
        text = source  # fall back to raw comparison
    return [ln.strip() for ln in text.split("\n") if ln.strip()]


def load(path):
    nb = nbformat.read(path, as_version=4)
    code = [normalise(c.source) for c in nb.cells if c.cell_type == "code"]
    n_md = sum(c.cell_type == "markdown" for c in nb.cells)
    return code, n_md


def compare(sl_path, en_path):
    sl_code, sl_md = load(sl_path)
    en_code, en_md = load(en_path)
    problems = []
    if len(sl_code) != len(en_code):
        problems.append(f"code cells: sl {len(sl_code)} vs en {len(en_code)}")
    if sl_md != en_md:
        problems.append(f"markdown cells: sl {sl_md} vs en {en_md}")
    for i, (a, b) in enumerate(zip(sl_code, en_code)):
        if a != b:
            line = next(
                (j for j, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b))
            )
            sl_l = a[line] if line < len(a) else "<missing>"
            en_l = b[line] if line < len(b) else "<missing>"
            problems.append(f"code cell #{i} differs at line {line + 1}: sl '{sl_l}' vs en '{en_l}'")
            break
    return problems


def notebooks_by_prefix(directory):
    result = {}
    if directory.is_dir():
        for p in sorted(directory.glob("*.ipynb")):
            m = PREFIX.match(p.name)
            if m:
                result[m.group(1)] = p
    return result


def last_commit_time(path):
    out = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", str(path)],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return int(out) if out else None


def main():
    drift = False
    sl, en = notebooks_by_prefix(SL_DIR), notebooks_by_prefix(EN_DIR)
    print("Notebooks (sl vs en):")
    for num in sorted(set(sl) | set(en)):
        if num not in en:
            print(f"  {num}: MISSING English counterpart for '{sl[num].name}'")
            drift = True
        elif num not in sl:
            print(f"  {num}: MISSING Slovenian counterpart for '{en[num].name}'")
            drift = True
        else:
            try:
                problems = compare(sl[num], en[num])
            except Exception as exc:  # unreadable notebook is a failure, not a pass
                problems = [f"cannot read notebook: {exc}"]
            if problems:
                drift = True
                print(f"  {num}: DRIFT - " + "; ".join(problems))
            else:
                print(f"  {num}: OK")

    print("Pages:")
    for sl_name, en_name in PAGES:
        sl_t, en_t = last_commit_time(BOOK / sl_name), last_commit_time(BOOK / en_name)
        if not (BOOK / en_name).exists():
            print(f"  {en_name}: MISSING")
            drift = True
        elif sl_t is not None and (en_t is None or sl_t > en_t):
            print(f"  WARNING {sl_name} was committed after {en_name}; check the translation")
        else:
            print(f"  {sl_name}: OK")

    print("Result:", "DRIFT FOUND" if drift else "all OK")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
