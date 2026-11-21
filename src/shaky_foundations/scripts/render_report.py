"""Render a markdown report to one self-contained HTML file (figures embedded as base64).

Image links in the markdown are resolved relative to the report and inlined, so the HTML shows its figures
anywhere (the figures themselves stay in the track figures folder; data/ is gitignored). Writes
<report>.html next to the markdown file.

    uv run --with markdown python src/shaky_foundations/scripts/render_report.py docs/reports/<dir>/report.md
"""

import argparse
import base64
import mimetypes
import re
from pathlib import Path

import markdown

CSS = """
:root { --ink:#1a1a19; --muted:#5f5e5a; --rule:#e3e2de; --surface:#ffffff; --tint:#f6f5f2; --accent:#2a78d6; }
body { background: var(--surface); color: var(--ink); margin: 0;
       font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
main { max-width: 860px; margin: 0 auto; padding: 48px 20px 96px; }
h1 { font-size: 30px; line-height: 1.25; margin: 0 0 12px; letter-spacing: -0.01em; }
h2 { font-size: 22px; margin: 48px 0 12px; padding-top: 12px; border-top: 1px solid var(--rule); }
h3 { font-size: 18px; margin: 32px 0 8px; }
p, li { max-width: 74ch; }
a { color: var(--accent); }
table { border-collapse: collapse; width: 100%; margin: 16px 0 24px; font-size: 14px; display: block; overflow-x: auto; }
th, td { text-align: left; vertical-align: top; padding: 7px 10px; border-bottom: 1px solid var(--rule); }
th { background: var(--tint); font-weight: 600; }
img { display: block; max-width: 100%; height: auto; margin: 24px auto 8px; }
p.caption { color: var(--muted); font-size: 14px; font-style: italic; }
p.caption em { font-style: normal; }
code { background: var(--tint); padding: 1px 5px; border-radius: 4px; font-size: 0.9em; }
pre { background: var(--tint); padding: 14px 16px; border-radius: 6px; overflow-x: auto; font-size: 13.5px; line-height: 1.5; }
pre code { background: none; padding: 0; }
blockquote { margin: 16px 0; padding: 4px 16px; border-left: 3px solid var(--rule); color: var(--muted); }
@media (max-width: 600px) { main { padding: 28px 16px 64px; } h1 { font-size: 24px; } }
"""


def inline_images(html: str, base: Path) -> str:
    def repl(m):
        src = m.group(2)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        path = (base / src).resolve()
        if not path.exists():
            raise FileNotFoundError(f"FATAL: image not found: {path}")
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        data = base64.b64encode(path.read_bytes()).decode()
        return f'{m.group(1)}data:{mime};base64,{data}{m.group(3)}'
    return re.sub(r'(<img[^>]*?src=")([^"]+)(")', repl, html)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report_path")
    args = parser.parse_args()

    md_path = Path(args.report_path)
    if not md_path.exists():
        raise FileNotFoundError(f"FATAL: {md_path} not found")
    text = md_path.read_text()
    title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), md_path.stem)
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    body = inline_images(body, md_path.parent)
    # Paragraphs that are entirely italic (figure captions, the subtitle line) get the caption style;
    # inline emphasis inside ordinary text is left alone.
    body = re.sub(r"<p><em>(.*?)</em></p>", r'<p class="caption">\1</p>', body, flags=re.DOTALL)
    html = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{title}</title><style>{CSS}</style></head>\n<body><main>\n{body}\n</main></body></html>\n')
    out = md_path.with_suffix(".html")
    out.write_text(html)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
