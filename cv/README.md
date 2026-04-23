# CV pipeline

Single-source CV: one YAML file (`cv.yaml`) is the canonical content; a build
script renders both the LaTeX source (`cv.tex` → `cv.pdf`) and the JSON
(`../_data/cv.json`) that the Jekyll site reads to render `/cv/`.

```
cv/cv.yaml                   # source of truth — edit here, only here
cv/templates/cv.tex.j2       # Jinja → LaTeX template
cv/build_cv.py               # renders both outputs
cv/cv.tex                    # GENERATED — do not hand-edit
cv/cv.pdf                    # GENERATED — committed for release
_data/cv.json                # GENERATED — read by Jekyll
```

## Rebuilding

Once, locally:

```bash
pip install pyyaml jinja2 --user        # or --break-system-packages on Debian/Ubuntu
```

Then, from the repo root:

```bash
python cv/build_cv.py            # writes cv/cv.tex and _data/cv.json
python cv/build_cv.py --compile  # also runs lualatex twice, producing cv/cv.pdf
```

Flags: `--tex-only`, `--json-only`, `--compile`.

## Typography setup

The LaTeX template uses three typefaces, per the project Visual Identity
Guide. All three are free/open licences; install them system-wide before
the first compile.

| Face       | Role                                   | Where to get it                                  |
|------------|----------------------------------------|--------------------------------------------------|
| Literata   | display, name, publication heads       | <https://fonts.google.com/specimen/Literata>     |
| Inter      | body, section heads, captions          | <https://rsms.me/inter/>                         |
| Fira Code  | monospace (code, package names, URLs)  | <https://github.com/tonsky/FiraCode/releases>    |

Install the TrueType files to your user fonts folder (macOS:
`~/Library/Fonts/`; Linux: `~/.fonts/`; Windows: right-click → Install). Run
`fc-cache -f` on Linux after copying. Confirm with
`fc-list | grep -iE 'literata|inter|fira code'`.

The template addresses Inter as `Inter` and expects weight variants
`Regular`, `Medium`, `Italic`, `Medium Italic`. Emphasis (`\textbf`) is
bound to **Medium (500)**, never Bold (700), in accordance with the identity
guide. If you install InterVariable instead of the static cuts, adjust the
`\setmainfont` block to use `InterVariable` and drop the per-weight font
declarations.

## Engine

Compile with **LuaLaTeX** (preferred) or XeLaTeX. Both support `fontspec`
and system-installed OpenType fonts. `pdflatex` will not work.

Two compilation passes are needed for the running footer (`n of N`) to pick
up the `\pageref{LastPage}` reference. The `--compile` flag runs both
passes automatically.

## Overleaf workflow

The ideal setup — and the one this pipeline is designed for — is a LaTeX CV
on Overleaf that links to this GitHub repo.

### Paid tier: GitHub sync (recommended)

1. Create a new Overleaf project, then import from GitHub. Point it at
   this repository.
2. In the Overleaf project, set the main document to `cv/cv.tex`.
3. Upload the three font families (Literata, Inter, Fira Code) to the
   project — Overleaf does not have them pre-installed.
   - You can drop TTFs directly into the project root; `fontspec` under
     LuaLaTeX will pick them up.
4. Set the compile engine to LuaLaTeX in *Menu → Settings → Compiler*.
5. When you want to update: edit `cv.yaml` locally, run
   `python cv/build_cv.py`, commit, push. Overleaf's GitHub sync picks up
   the regenerated `cv.tex` on the next pull.

### Free tier: Git bridge

Overleaf's free tier offers a read-only Git clone URL per project
(*Menu → Git*). You can then push from a local clone of the Overleaf
project, but you can't bi-directionally sync with GitHub. Workflow:

1. Create an Overleaf project and upload `cv/cv.tex` plus the three font
   families.
2. Clone the Overleaf-provided git URL locally.
3. When content changes: regenerate `cv.tex` in this repo, copy to the
   Overleaf clone, push. Or: copy `cv.yaml` + the template + the script
   into the Overleaf project and run the build there — but Overleaf can't
   execute Python during compile, so this requires a compile-time hack
   (e.g. `\write18` which Overleaf disables). Stick with option 1.

### Alternatives

If you'd rather skip Overleaf entirely, GitHub Actions can compile the CV
on push: run `python cv/build_cv.py --compile` inside a TeXLive container
and commit or release `cv/cv.pdf`. Not implemented here, but the pipeline
is clean enough to drop into a workflow file when you want it.

## How the Jekyll CV page is kept in sync

The Jekyll `/cv/` page (`_pages/cv.md` → `_includes/cv-template.html`)
reads `_data/cv.json`. `build_cv.py` emits that JSON in the JSON Resume
shape the include already expects — `basics`, `education`, `work`,
`skills`, `publications`, `presentations`, `teaching`, `portfolio`,
`languages`, `references`. Not every YAML section has a JSON counterpart
(e.g. invited talks are folded into `presentations`; R packages and public
repos are folded into `portfolio`), but the set is wide enough that the
web CV page stays reasonably comprehensive.

If you want to add or reshape a field: edit `cv.yaml`, adjust
`build_cv.py`'s `build_json()` to surface it, and — if the field should
appear in the LaTeX CV too — extend `templates/cv.tex.j2`.

## Jinja delimiters

The template uses non-default Jinja delimiters to avoid collision with
LaTeX syntax (which eats `{}` and `%`):

| Jinja construct | Delimiter in this project |
|-----------------|---------------------------|
| `{% block %}`   | `((* block *))`           |
| `{{ var }}`     | `((( var )))`             |
| `{# comment #}` | `((# comment #))`         |

A consequence: if you need a **literal** `(` immediately before a Jinja
variable opener, insert an empty LaTeX group `{}` to break the
tokenisation, e.g. `({}((( var )))`. Otherwise Jinja will greedily match
four opens as `(((` + `(` and trip over unmatched parens.

## Filters available in the template

All defined in `build_cv.py`:

- `|tex` — LaTeX-escape a plain string (`& % $ # _ { } ~ ^ \`).
- `|markdown_to_tex` — escape and convert lightweight markdown: `**bold**`
  → `\textbf{…}`; `*italic*` → `\textit{…}`; `[text](url)` → `\href{…}{…}`.
- `|emph_author` — wrap the author's own name in `**…**` markers so the
  downstream `markdown_to_tex` bolds it. Apply before `markdown_to_tex`.
- `|strip_scheme` — `https://foo/` → `foo`.
- `|strip_github` — `https://github.com/User/Repo` → `User/Repo`.
- `|strip_trailing_dot` — drops a trailing full stop.
- `|join_commas`, `|join_semi` — join a list with `, ` or `; `.

## Colours and sizing (for reference)

Set in the template preamble; keep in sync with the Visual Identity Guide.

| Token         | Hex      | Role                                      |
|---------------|----------|-------------------------------------------|
| `burntred`    | `#9E2A1E`| Name band, section-head accent            |
| `bottlegreen` | `#1E3A34`| Defined but unused on the CV              |
| `deepmaroon`  | `#681F34`| Links, link-hover                         |
| `pagecream`   | `#FAF7F2`| Page background                           |
| `ink`         | `#2B2A26`| Body text                                 |
| `inkmuted`    | `#6C6A64`| Dates, meta labels, running header/footer |
| `rulegrey`    | `#E5E0D5`| Hairline under section titles             |
| `creamonred`  | `#FBEDE8`| Name and tagline on red band              |

Body: Inter Regular 10.5 pt, leading 1.55. Section heads: Inter Medium
small-caps 11 pt, tracked +0.14 em, burnt red. Name: Literata SemiBold
21 pt, cream-on-red. Links: deep maroon, no underline.

## Troubleshooting

**`fontspec` error — font not found.** Install the font system-wide, or
on Overleaf upload the TTF into the project. If the variant name (e.g.
`Inter Medium`) isn't picked up, drop the `BoldFont = * Medium` line and
rely on fontspec's own bold substitution, which will look less sharp but
will compile.

**`luaotfload-main not found` under LuaLaTeX.** The TeX Live install is
incomplete; add `texlive-latex-extra` (Debian/Ubuntu) or `scheme-full`.
Or switch the first-line `TS-program` marker to `xelatex`.

**Extra `(` in output.** The Jinja `(((` collision described above — add
`{}` between a literal `(` and the variable opener.

**Running footer reads `n of ??`**. Second compile pass wasn't run. Use
`--compile` or `latexmk -lualatex cv.tex`.
