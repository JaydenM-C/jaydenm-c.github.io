#!/usr/bin/env python3
"""
Build script for the CV shared-source pipeline.

Reads     cv/cv.yaml   (single source of truth, edited by hand)
Writes    cv/cv.tex    (LaTeX source, rendered from cv/templates/cv.tex.j2)
Writes    _data/cv.json (JSON consumed by _includes/cv-template.html)

Usage:
    python cv/build_cv.py

Optional flags:
    --tex-only     skip the JSON emitter
    --json-only    skip the LaTeX emitter
    --compile      after rendering, invoke `lualatex` twice in cv/ so the
                   running header picks up the page-count reference.

Dependencies: PyYAML, Jinja2.  Install with:
    pip install pyyaml jinja2 --break-system-packages
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML is required: pip install pyyaml\n")
    sys.exit(1)

try:
    from jinja2 import Environment, FileSystemLoader, ChainableUndefined
except ImportError:
    sys.stderr.write("Jinja2 is required: pip install jinja2\n")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CV_DIR        = Path(__file__).resolve().parent
REPO_ROOT     = CV_DIR.parent
YAML_PATH     = CV_DIR / "cv.yaml"
TEMPLATE_DIR  = CV_DIR / "templates"
TEX_OUTPUT    = CV_DIR / "cv.tex"
JSON_OUTPUT   = REPO_ROOT / "_data" / "cv.json"

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
_TEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "{":  r"\{",
    "}":  r"\}",
    "&":  r"\&",
    "%":  r"\%",
    "$":  r"\$",
    "#":  r"\#",
    "_":  r"\_",
    "~":  r"\textasciitilde{}",
    "^":  r"\textasciicircum{}",
}


def tex_escape(value) -> str:
    """Escape a plain string for LaTeX. Leaves markdown intact (handled
    separately by markdown_to_tex). Backslash first to avoid double-escape."""
    if value is None:
        return ""
    s = str(value)
    # order matters: backslash first
    out = []
    for ch in s:
        out.append(_TEX_ESCAPES.get(ch, ch))
    return "".join(out)


_MD_BOLD_RE   = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC_RE = re.compile(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)")
_MD_LINK_RE   = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
# Bare URL: http(s)://… up to the next whitespace, bracket, or terminal
# punctuation. Trailing `.,;:` is left outside \url{...} so LaTeX can break
# the line on it. No negative lookbehind needed: markdown links were already
# replaced by placeholders above this in the pipeline, so every match here
# is a genuine bare URL in prose (including ones wrapped in parens like
# "foo (https://…)").
_BARE_URL_RE  = re.compile(r"(https?://[^\s<>()\[\]]+[^\s<>()\[\].,;:])")


def markdown_to_tex(value) -> str:
    """Convert a lightweight markdown-flavoured string to LaTeX.

    Handles **bold**, *italic*, [text](url). Everything else is tex-escaped.
    Order: extract links first (so their URL isn't escaped), then bold, then
    italic, then escape what's left.
    """
    if value is None:
        return ""
    s = str(value)

    # Use ASCII-only sentinels that contain no LaTeX specials so they survive
    # tex_escape verbatim. Must not appear in source content.
    SENT_B_OPEN   = "@@@MDBO@@@"
    SENT_B_CLOSE  = "@@@MDBC@@@"
    SENT_I_OPEN   = "@@@MDIO@@@"
    SENT_I_CLOSE  = "@@@MDIC@@@"

    # Protect raw URLs inside markdown links by replacing with placeholders.
    placeholders = []

    def _link_sub(m):
        text, url = m.group(1), m.group(2)
        idx = len(placeholders)
        placeholders.append((text, url))
        return f"@@@MDLK{idx}@@@"

    s = _MD_LINK_RE.sub(_link_sub, s)

    # Bare URLs — caught *after* markdown-link extraction so the URLs inside
    # `[text](url)` (already replaced by placeholders above) can't double-match.
    # Wrapping in \url{} lets LaTeX (with xurl loaded) break long URLs at
    # slashes / dots, fixing the overfull-hbox warnings for raw links.
    bare_urls: list[str] = []

    def _bare_url_sub(m):
        url = m.group(1)
        idx = len(bare_urls)
        bare_urls.append(url)
        return f"@@@MDBU{idx}@@@"

    s = _BARE_URL_RE.sub(_bare_url_sub, s)

    # Bold / italic markers — swap to sentinels to survive tex-escape.
    s = _MD_BOLD_RE.sub(lambda m: SENT_B_OPEN + m.group(1) + SENT_B_CLOSE, s)
    s = _MD_ITALIC_RE.sub(lambda m: SENT_I_OPEN + m.group(1) + SENT_I_CLOSE, s)

    # Tex-escape the remainder. Sentinels are pure ASCII letters/@, untouched.
    s = tex_escape(s)

    # Restore formatting.
    s = s.replace(SENT_B_OPEN, r"\textbf{").replace(SENT_B_CLOSE, "}")
    s = s.replace(SENT_I_OPEN, r"\textit{").replace(SENT_I_CLOSE, "}")

    # Restore links.
    def _restore_link(m):
        idx = int(m.group(1))
        text, url = placeholders[idx]
        return r"\href{" + url + "}{" + tex_escape(text) + "}"
    s = re.sub(r"@@@MDLK(\d+)@@@", _restore_link, s)

    # Restore bare URLs as \url{} — unescaped, xurl handles the line-breaking.
    def _restore_bare_url(m):
        idx = int(m.group(1))
        return r"\url{" + bare_urls[idx] + "}"
    s = re.sub(r"@@@MDBU(\d+)@@@", _restore_bare_url, s)

    return s


_AUTHOR_SELF = [
    "Macklin-Cordes, Jayden L.",
    "Jayden L. Macklin-Cordes",
]


def emph_author(value) -> str:
    """Bold the author's own name inside a byline string.

    Applied *before* markdown_to_tex: we inject **...** markers so the
    downstream filter converts them to \textbf{}. This keeps the escape
    pipeline consistent."""
    if value is None:
        return ""
    s = str(value)
    for needle in _AUTHOR_SELF:
        s = s.replace(needle, f"**{needle}**")
    return s


def strip_scheme(value) -> str:
    """https://foo/ → foo, for display-friendly URL rendering."""
    if value is None:
        return ""
    s = str(value)
    s = re.sub(r"^https?://", "", s)
    return s.rstrip("/")


def strip_github(value) -> str:
    """https://github.com/User/Repo → User/Repo."""
    if value is None:
        return ""
    s = str(value)
    s = re.sub(r"^https?://github\.com/", "", s)
    return s.rstrip("/")


def strip_trailing_dot(value) -> str:
    if value is None:
        return ""
    return str(value).rstrip(". ")


def join_commas(items) -> str:
    return ", ".join(str(i) for i in (items or []))


def join_semi(items) -> str:
    return "; ".join(str(i) for i in (items or []))


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------
def build_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        # Custom delimiters — avoid collision with LaTeX {} and % syntax.
        block_start_string="((*",
        block_end_string="*))",
        variable_start_string="(((",
        variable_end_string=")))",
        comment_start_string="((#",
        comment_end_string="#))",
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=ChainableUndefined,
        autoescape=False,
        keep_trailing_newline=True,
    )
    env.filters["tex"]              = tex_escape
    env.filters["markdown_to_tex"]  = markdown_to_tex
    env.filters["emph_author"]      = emph_author
    env.filters["strip_scheme"]     = strip_scheme
    env.filters["strip_github"]     = strip_github
    env.filters["strip_trailing_dot"] = strip_trailing_dot
    env.filters["join_commas"]      = join_commas
    env.filters["join_semi"]        = join_semi
    return env


def render_tex(data: dict) -> str:
    env = build_env()
    template = env.get_template("cv.tex.j2")
    return template.render(**data)


# ---------------------------------------------------------------------------
# JSON emitter — shapes cv.yaml into the JSON Resume-ish schema the existing
# Jekyll include (_includes/cv-template.html) already reads. We fill the
# fields the template iterates and leave gracefully missing fields empty.
# ---------------------------------------------------------------------------
def _strip_markdown(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    s = _MD_BOLD_RE.sub(r"\1", s)
    s = _MD_ITALIC_RE.sub(r"\1", s)
    s = _MD_LINK_RE.sub(r"\1 (\2)", s)
    return s.strip()


def build_json(data: dict) -> dict:
    basics = data["basics"]
    out = {
        "basics": {
            "name":    basics["name"],
            "label":   basics["label"],
            "email":   basics["email"],
            "website": basics["website"],
            "summary": _strip_markdown(data.get("research_profile", "")),
            "location": {
                "city":        "Guildford",
                "region":      "Surrey",
                "countryCode": "UK",
            },
            "profiles": [
                {"network": "GitHub",
                 "url": "https://github.com/JaydenM-C",
                 "username": "JaydenM-C"},
                {"network": "Orcid",
                 "url": basics["orcid_url"],
                 "username": basics["orcid"]},
            ],
        },
        "work": [
            {
                "company":   j["institution"],
                "position":  j["role"] + (f" ({j['role_note']})" if j.get("role_note") else ""),
                "startDate": j.get("start_date", ""),
                "endDate":   j.get("end_date", ""),
                "summary":   j.get("department", ""),
                "highlights": [j["project"]] if j.get("project") else [],
            }
            for j in data.get("professional_experience", [])
        ],
        "education": [
            {
                "institution": e["institution"],
                "area":        e["degree"],
                "studyType":   e["degree"],
                "endDate":     e.get("date", ""),
                "gpa":         "",
                "courses":     e.get("details", []) or [],
            }
            for e in data.get("education", [])
        ],
        "skills": [
            {
                "name":     s["label"],
                "level":    "",
                "keywords": [_strip_markdown(s["text"])],
            }
            for s in data.get("skills", [])
        ],
        "publications": [
            {
                "name":        _strip_markdown(p["title"]).rstrip(". "),
                "publisher":   _strip_markdown(p.get("venue", "")),
                "releaseDate": (p["year"] if re.match(r"^\d{4}$", str(p.get("year", ""))) else ""),
                "summary":     _strip_markdown(p.get("authors", "")),
                "website":     p.get("doi", ""),
            }
            for p in data.get("publications", [])
        ],
        "presentations": [
            {
                "name":        _strip_markdown(p["title"]).rstrip(". "),
                "event":       _strip_markdown(p.get("venue", "")),
                "date":        (p.get("year_text") or "")[:4]
                                  if re.match(r"^\d{4}",
                                              str(p.get("year_text", "")))
                                  else "",
                "location":    "",
                "description": _strip_markdown(p.get("authors", "")),
            }
            for p in (data.get("conference_presentations", []) +
                      data.get("invited_talks", []))
        ],
        "teaching": [
            {
                "course":      f"{c['code']} {c['title']}",
                "institution": block["institution"],
                "date":        (entry["term"].split(",")[0].strip()
                                 if isinstance(entry["term"], str) else ""),
                "role":        c.get("role", "Lecturer"),
                "description": f"{c.get('level', '')}"
                                 + (f", {c.get('students')} students"
                                    if c.get("students") else ""),
            }
            for block in data.get("teaching", {}).get("courses_taught", [])
            for entry in block["entries"]
            for c in entry["courses"]
        ],
        "portfolio": [
            {
                "name":        p["name"],
                "category":    "r-package",
                "date":        "",
                "description": _strip_markdown(p["description"]),
                "url":         p["url"],
            }
            for p in data.get("r_packages", [])
        ] + [
            {
                "name":        strip_github(r["url"]),
                "category":    "repository",
                "date":        "",
                "description": _strip_markdown(r["description"]),
                "url":         r["url"],
            }
            for r in data.get("public_repos", [])
        ],
        "languages": [
            {
                "language": item.split(" (")[0] if " (" in item else item,
                "fluency":  (item.split(" (")[1].rstrip(")")
                             if " (" in item else ""),
            }
            for item in data.get("language_proficiencies", [])
        ],
        "interests": [],
        "references": [
            {
                "name":      r["name"],
                "reference": f"{r['title']}. "
                              + ". ".join(r["lines"])
                              + f". {r['email']}",
            }
            for r in data.get("referees", [])
        ],
    }
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tex-only",  action="store_true")
    ap.add_argument("--json-only", action="store_true")
    ap.add_argument("--compile",   action="store_true",
                    help="Run `lualatex` twice on the generated cv.tex")
    args = ap.parse_args()

    if not YAML_PATH.exists():
        sys.stderr.write(f"Source YAML not found: {YAML_PATH}\n")
        return 1

    with YAML_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    if not args.json_only:
        tex = render_tex(data)
        TEX_OUTPUT.write_text(tex, encoding="utf-8")
        print(f"wrote {TEX_OUTPUT.relative_to(REPO_ROOT)}")

    if not args.tex_only:
        JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with JSON_OUTPUT.open("w", encoding="utf-8") as fh:
            json.dump(build_json(data), fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print(f"wrote {JSON_OUTPUT.relative_to(REPO_ROOT)}")

    if args.compile:
        if shutil.which("lualatex") is None:
            sys.stderr.write("lualatex not found on PATH; skipping compile.\n")
            return 2
        for pass_n in (1, 2):
            r = subprocess.run(
                ["lualatex", "-interaction=nonstopmode",
                 "-halt-on-error", "cv.tex"],
                cwd=CV_DIR,
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                sys.stderr.write(
                    f"lualatex pass {pass_n} failed:\n{r.stdout[-2000:]}\n")
                return 3
        print(f"compiled {(CV_DIR / 'cv.pdf').relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
