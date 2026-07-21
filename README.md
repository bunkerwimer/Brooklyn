# Brooklyn

A WIDA-aligned **English Language Development (ELD)** curriculum for secondary newcomers
(grades 6–12), built so that one authored objective renders to a print packet, a projector
routine, or a device task. Print is a first-class output, not an afterthought.

**Start here:** open `docs/brooklyn-browser.html` in a browser. Pick a unit, tick the pages
you need, print exactly those.

---

## What's in the box

| Path | What it is |
|---|---|
| `curriculum/units/u01…u12.json` | **Source of truth.** 12 units, 48 objective cards, 144 leveled variants. |
| `curriculum/SCHEMA.md` | The Objective Card schema. **Read this before authoring.** |
| `curriculum/standards/frameworks.json` | WIDA / CA ELD / TX ELPS / NY metadata + crosswalk. |
| `docs/brooklyn-browser.html` | The teacher app — drill-down navigation and a print tray. |
| `docs/brooklyn-curriculum.html` | The whole curriculum as one reference page. |
| `docs/brooklyn-scope-and-sequence.html` | The pitch doc (hand-authored). |
| `prototypes/brooklyn-objective-card.html` | One card rendering to print *and* device. |
| `tools/` | Validation and build scripts. Python 3 stdlib only. |
| `index.html` | Landing page. |

## Setup

You need **Python 3** and **git**. That's it — no Node, no `npm install`, no database, no
API keys. macOS and most Linux ship Python 3 already; on Windows install it from
[python.org](https://python.org) and tick *"Add Python to PATH"*.

```bash
git clone git@github.com:bunkerwimer/Brooklyn.git
cd Brooklyn
python3 tools/validate.py     # should print "All units valid."
```

If `python3` isn't found on Windows, use `py -3` instead everywhere below.

## The one workflow rule

**Curriculum content is data, never HTML.** Everything in `docs/` is generated. If you
hand-edit `brooklyn-browser.html` or `brooklyn-curriculum.html`, the next build silently
erases your work.

To change curriculum:

```bash
# 1. edit the JSON
#    curriculum/units/u03.json

# 2. validate, then rebuild both outputs
python3 tools/validate.py && python3 tools/build_docs.py && python3 tools/build_app.py

# 3. open docs/brooklyn-browser.html and look at what you changed

# 4. commit
git add -A && git commit -m "Unit 03: …" && git push
```

`validate.py` exits non-zero on error, so it's safe to chain with `&&`. It checks the schema,
card IDs, WIDA values, level progression, and that the prototype hasn't drifted from the
curriculum. Run it before every commit.

The exception: `docs/brooklyn-scope-and-sequence.html` and `prototypes/` are hand-authored and
safe to edit directly. (The scope-and-sequence doc duplicates content that also lives in
`curriculum/units/` — a known issue, see the repo history.)

## Deployment

Pushing to `main` triggers a Vercel deploy automatically. The site is static; `index.html` is
served at the root.

## Status and honest limits

- **Pre-review.** The curriculum has not yet been reviewed by credentialed EL/TESOL educators.
  Review is in progress. Mastery thresholds in each `check` (e.g. "4 of 5 trials") are
  placeholders pending that review.
- **WIDA levels 1–3** of 6, covering **~24 weeks**, **secondary (6–12) newcomers only**.
- **No images yet.** Many Level 1 scaffolds call for picture support that has not been
  produced. Student pages render an explicit placeholder so the gap is visible rather than
  hidden. This is the biggest blocker to classroom use.
- The standards crosswalk in `frameworks.json` is **unvalidated** and marked as such in the
  file and on the rendered page. It must be checked against each state's current documents
  before being shown to a district in that state.

## Standards note

Independent alignment to the WIDA ELD Standards Framework (2020). Not affiliated with,
authorized by, or endorsed by WIDA or the University of Wisconsin.
