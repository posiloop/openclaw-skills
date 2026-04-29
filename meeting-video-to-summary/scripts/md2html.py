#!/usr/bin/env python3
"""Convert summary.md to summary.html with table + heading support.

Usage: md2html.py <input.md> <output.html>
"""
import sys
import markdown

if len(sys.argv) != 3:
    print("Usage: md2html.py <input.md> <output.html>", file=sys.stderr)
    sys.exit(1)

src, dst = sys.argv[1], sys.argv[2]

with open(src, "r", encoding="utf-8") as f:
    md_text = f.read()

html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "sane_lists"],
)

# Wrap in a minimal HTML skeleton so Google Drive recognises it for conversion
html_doc = (
    "<!DOCTYPE html>\n"
    "<html><head><meta charset=\"utf-8\"></head><body>\n"
    + html_body
    + "\n</body></html>\n"
)

with open(dst, "w", encoding="utf-8") as f:
    f.write(html_doc)

print(f"[ok] wrote {dst} ({len(html_doc)} bytes)")
