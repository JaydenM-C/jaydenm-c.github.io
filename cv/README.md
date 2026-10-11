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

The LaTeX template uses the Newy Sunsets typefaces, loaded **by file**
from `cv/fonts/`. No system-wide install required — the fonts are
committed into the repo and travel with it, so Overleaf and any clone of
the repo compile identically.

| Face          | Role                                              |
|---------------|---------------------------------------------------|
| Newsreader    | body, emphasis (italic), bold for names/roles     |
| Jost          | name (21 pt), section heads, subsection heads     |
| IBM Plex Mono | dates, running header/footer, package names, URLs |

```
cv/fonts/
├── Newsreader-Text-Regular.ttf
├── Newsreader-Text-Italic.ttf
├── Newsreader-Text-SemiBold.ttf        ← \textbf
├── Newsreader-Text-SemiBoldItalic.ttf
├── Jost-Regular.ttf
├── Jost-Medium.ttf                     ← name, section heads
├── Jost-SemiBold.ttf
└── IBMPlexMono-Regular.ttf
```

The Newsreader and Jost files are **static instances generated from the
variable fonts** in the Newy Sunsets `fonts/` folder (fontTools
`varLib.instancer`): Newsreader at optical size 10.5 (matching the 10.5 pt
body, per the identity guide's "opsz ≈ point size" rule) at weights 400
and 600; Jost at 400, 500 and 600. LuaLaTeX can't reliably drive
Newsreader's opsz axis, so pinning it in a static cut is the robust way to
get the right optical size. To regenerate, e.g. for a different body size:

```python
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
f = TTFont("Newsreader-VariableFont_opsz-wght.ttf")
instancer.instantiateVariableFont(f, {"wght": 400, "opsz": 10.5}).save("Newsreader-Text-Regular.ttf")
```

(Give each instance a distinct family/PostScript name in its `name`
table so font caches don't confuse them.) All fonts are SIL OFL 1.1.

The old Jaydencore files (Inter, Literata, Fira Code) are no longer used
and can be deleted.

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
2. In the Overleaf project, set *Main document* to `cv/cv.tex`
   (*Menu → Settings → Main document*). This also sets the compile
   working directory to `cv/`, which is what the `Path = fonts/` font
   declarations expect.
3. Set the compile engine to LuaLaTeX in *Menu → Settings → Compiler*.
4. The font files in `cv/fonts/` (see Typography setup above) are pulled
   with the repo, so nothing else to upload.
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

Set in the template preamble; keep in sync with the Newy Sunsets guide.

| Token           | Hex       | Role                                           |
|-----------------|-----------|------------------------------------------------|
| `deeppacific`   | `#284958` | Name band                                      |
| `whitewater`    | `#91ADBE` | Tagline on the band                            |
| `paper`         | `#FFFEF9` | Page background; name on the band              |
| `coal`          | `#181414` | Body text                                      |
| `siltstone`     | `#706468` | Dates, meta labels, running header/footer      |
| `sandstone`     | `#AE4E1B` | Section heads, bullets                         |
| `federationred` | `#841C1B` | Links, awards, amounts, evaluations            |
| `tuff`          | `#D9D8D6` | Hairline under section titles                  |

Body: Newsreader 10.5 pt (opsz 10.5), leading ≈ 1.5. Section heads: Jost
Medium tracked capitals (+0.14 em), 9.5 pt, Sandstone — Jost has no true
small caps, so reduced-size capitals stand in. Name: Jost Medium 21 pt,
Paper on Deep Pacific (one weight lighter than on a light field, per the
guide). Dates and running chrome: IBM Plex Mono, Siltstone. Links:
Federation Red, no underline.

## Troubleshooting

**`fontspec` error — font not found.** Check the eight files listed under
Typography setup are in `cv/fonts/` with exactly those names (on
Overleaf, that they were pulled or uploaded into the project).

**`File scrartcl.cls not found` (or another `.sty`/`.cls`).** A minimal
TeX install (TinyTeX, BasicTeX) is missing a package. Install it with
`tlmgr install <package>`; `tlmgr search --global --file <name>` finds
which package provides a file. The set this template needs:
`koma-script babel-english fontspec lm microtype xcolor geometry fancyhdr
pgf lastpage enumitem titlesec etoolbox xurl tools hyperref`.

**`luaotfload-main not found` under LuaLaTeX.** The TeX Live install is
incomplete; add `texlive-latex-extra` (Debian/Ubuntu) or `scheme-full`.
Or switch the first-line `TS-program` marker to `xelatex`.

**Extra `(` in output.** The Jinja `(((` collision described above — add
`{}` between a literal `(` and the variable opener.

**Running footer reads `n of ??`**. Second compile pass wasn't run. Use
`--compile` or `latexmk -lualatex cv.tex`.
