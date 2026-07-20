# Brooklyn

> **Standalone venture.** Completely separate from the "Bunker's Presentation software" / Groundwork
> real-estate & zoning project. Do NOT mix code, data, memory, or context between the two. Nothing
> from the zoning project belongs here, and nothing here belongs there.

**Everything in this project is labeled "Brooklyn"** — repo, docs, prototypes, file names, artifacts.
"Newcomer ELD" is a description of what Brooklyn does, not its name.

## What this is
Brooklyn is a Duolingo-style **English Language Development (ELD)** learning platform + curriculum,
built to be **sold to K-12 school districts**. AI-driven, with **print materials as a first-class
output** because districts are banning classroom screen time.

## Confirmed product decisions (discovery, 2026-07-17)
- **Standards:** WIDA is primary (~40 states) but is **not** CA, TX, NY, or AZ — a large share of US
  ELs by headcount. A crosswalk lives in `curriculum/standards/frameworks.json`; it is **unvalidated**
  and must be reviewed by someone holding each state's documents. Anchor on **Standard 1 (Social & Instructional)** +
  **Standard 2 (Language Arts)**; grade clusters 6–8 / 9–12; proficiency **levels 1–3**.
- **Wedge / MVP:** secondary **newcomers** (grades 6–12, recently arrived). Scope = **Survival + ELD**
  across all four domains (Listening, Speaking, Reading, Writing).
- **Learners:** highly multilingual; **many SLIFE** (limited/interrupted formal education). Design is
  **oral-first, visual, low-text-load**, with **language-agnostic scaffolds** (an L1 "bridge" slot) and
  a parallel **foundational-literacy strand**.
- **Delivery-agnostic** is a core requirement — must support push-in, pull-out, newcomer class, blended,
  and self-serve, because each teacher's class structure differs. One content core renders as print
  packet / projector routine / device task / small-group cards.
- **AI priority #1 = personalize to proficiency** (which depends on generating leveled variants underneath).

## Content model — the Objective Card (the moat)
One authored object is the unit of everything:
`{ unit, WIDA standard, domain (L/S/R/W), key use, function, grammar, {L1,L2,L3 variants},
vocabulary, scaffolds, render targets, check }`.
- The **personalization engine** places a student on a WIDA level *per domain* and serves the matching variant.
- The **same card** compiles to a printable PDF, a projector slide, or an interactive task — so print-first
  and 1:1 districts buy the same product.
- Each **check** is **formative evidence** a teacher records. It is NOT a measure of proficiency-level
  movement — that is the state summative's job (ACCESS/ELPAC/TELPAS/NYSESLAT). Growth reporting is
  the administrator's buying trigger, but claiming level movement without validity evidence is a
  credibility and compliance risk. Frame as progress toward Can-Do descriptors.

## Repo layout
```
curriculum/SCHEMA.md        the Objective Card schema — read this before authoring
curriculum/units/u01..u12   SOURCE OF TRUTH. All 12 units, one file each.
tools/validate.py           schema + progression checks; exits non-zero on error
tools/build_docs.py         curriculum/ → docs/brooklyn-curriculum.html (reference, one page)
tools/build_app.py          curriculum/ → docs/brooklyn-browser.html (teacher app)
docs/                       generated + hand-authored docs (see note below)
prototypes/                 working proofs
```

**Curriculum content is data, never HTML.** Edit `curriculum/units/*.json`, then:
```bash
python3 tools/validate.py && python3 tools/build_docs.py && python3 tools/build_app.py
```
No Node in this environment — tooling is Python 3 (stdlib only, no install step).
`docs/brooklyn-curriculum.html` is build output; never hand-edit it.

## Status
- Approach chosen: **curriculum first**, before building software.
- **All 12 units authored** → `curriculum/units/`. 48 objective cards, 144 leveled variants.
  Each unit carries a domain × level can-do matrix with a scaffold and a check per cell, plus target
  structures, core/academic vocabulary, a foundational-literacy strand, a teaching note, and a worked
  task at all three levels. Validated clean by `tools/validate.py`.
- **Curriculum browser built** → `docs/brooklyn-browser.html`. The teacher-facing surface and the
  landing page's primary entry: Units → Unit → Page, with a **print tray** that collects pages across
  any units and prints exactly those. Student / Teacher / Both output, copies multiplier, tray persists
  in localStorage. Self-contained single file (curriculum inlined — `file://` can't `fetch()`).
  Driven end-to-end in-browser 2026-07-20: cross-unit selection, per-unit clear, mode switching,
  copies, print CSS parsed, zero console errors, AA-clean in both themes at mobile and desktop.
- **Curriculum reference generated** → `docs/brooklyn-curriculum.html`. Verified in-browser
  2026-07-20: 12 units, 48 domain rows, 144 leveled cells, 36 worked-task cards, both color schemes,
  no page-level horizontal overflow (wide tables scroll inside their own container).
- **Objective Card prototype done and verified** → `prototypes/brooklyn-objective-card.html`.
  One source card rendering to both print packet and device task. Verified in-browser 2026-07-20:
  level switch (L1/L2/L3) and surface switch (device/print) both work and compose correctly; no
  console errors. Fixed a malformed CSS rule (a selector list ran into an `@media` block) that was
  dropping the dark-mode pressed-chip color.

## Hard gates before any district sees this
1. **Credentialed review.** No licensed EL/TESOL educator has reviewed any of the 144 variants. Every
   mastery threshold ("4 of 5 trials") was authored without a basis and will change under review.
2. **Standards crosswalk validation** — see `curriculum/standards/frameworks.json`.
3. **Legal review** of the teaching notes. They touch mandated reporting, immigration, and health.
   Unit 08 previously asserted that calling 911 carries no immigration consequence; that claim was
   removed 2026-07-20 because it varies by jurisdiction. Others need counsel's eyes.
4. **Privacy paperwork**: SDPC National Data Privacy Agreement, NY Ed Law 2-d, IL SOPPA, CA AB1584.
5. **ESSA evidence tier + logic model** — Title III money increasingly asks for it. We are Tier 4.
6. **VPAT / Section 508.** Contrast is now AA-clean (verified in-browser, both themes, 2072 text
   nodes, zero failures) but keyboard nav and screen-reader semantics are untested.

## Coverage honesty (what "K-12 platform" does not yet mean)
- WIDA **levels 1–3 of 6**. Most ELs in a district sit at 3–5.
- **24 weeks** of a ~36-week year.
- **Secondary (6–12) newcomers only.** Elementary is different work. Do not demo this as "K-12".

## Known duplication (worth fixing before the content grows)
Two places still hold copies of curriculum content instead of reading it:

1. **`docs/brooklyn-scope-and-sequence.html`** — the hand-designed **pitch** doc. It hand-codes the
   12-unit grid and the Unit 01 exemplar, so that content exists there *and* in `curriculum/units/`.
   Fix by having `build_docs.py` emit those two sections as fragments injected between marker comments.
2. **`prototypes/brooklyn-objective-card.html`** — hardcodes its own u01 Speaking card, because a
   `file://` page can't `fetch()` the JSON. This **already drifted** (2026-07-20): the card id was
   `u01-speaking-introduce` and the L3 can-do had lost the word "back". Both realigned to the
   curriculum, and `validate.py` now fails if they diverge again. Real fix: generate the prototype's
   card at build time, which requires extending the schema to carry render details (listen prompts,
   build blanks, speech models) the curriculum doesn't hold yet.

**`Brooklyn Unit 1.pdf` is stale** — it was printed before the id fix, so its footer still reads
`u01-speaking-introduce`. Reprint from the prototype (Level 1 → Print packet → Print / Save as PDF).

## Content gaps that matter more than code
1. **No images.** Nearly every L1 scaffold says "picture support" / "photo cards" / "picture strip"
   and we ship zero images. A Level 1 newcomer packet without pictures is not usable. The browser's
   student pages render an explicit "Picture support goes here — not yet produced" slot so the gap is
   visible on every page rather than hidden. This is the single biggest blocker to classroom use.
2. **No day-by-day.** A unit is a 2-week spec, not a lesson plan. Teachers will ask what to do Monday.
3. **Vocabulary is a flat list**, not printable word cards / word-bank artifacts.
4. Student-facing "I can…" statements are derived at render time from `canDo`. All 144 convert cleanly,
   but a reviewer should check the wording rather than trusting the transform.

## Next steps
1. Fix the pitch-doc duplication above.
2. Spec **WIDA growth reporting** — how a `check` becomes level-movement evidence. Every check is
   already authored; nothing specifies the rollup yet.
3. Extend the prototype to render a second domain (it only does Speaking) to prove the content model
   generalizes across Listening/Reading/Writing.
4. Pilot-ready packet: compile one full unit to print and put it in front of a real EL teacher.

## Open / not yet decided
- Tech stack (currently curriculum data + Python tooling + a static prototype).
- Pilot / design-partner district.
- Compliance: FERPA, COPPA (under-13), rostering (Clever/ClassLink), SSO.
- Team.

## Standards note
Independent alignment to the WIDA ELD Standards Framework (2020). Not affiliated with, authorized by, or
endorsed by WIDA / the University of Wisconsin. Keep this disclaimer on anything shown to districts.
