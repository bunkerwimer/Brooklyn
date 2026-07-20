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
- **Standards:** WIDA framework (~40 states). Anchor on **Standard 1 (Social & Instructional)** +
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
- Each **check** emits WIDA level-movement **evidence** that rolls up into teacher/admin growth dashboards
  (the administrator's buying trigger).

## Repo layout
```
curriculum/SCHEMA.md        the Objective Card schema — read this before authoring
curriculum/units/u01..u12   SOURCE OF TRUTH. All 12 units, one file each.
tools/validate.py           schema + progression checks; exits non-zero on error
tools/build_docs.py         curriculum/ → docs/brooklyn-curriculum.html
docs/                       generated + hand-authored docs (see note below)
prototypes/                 working proofs
```

**Curriculum content is data, never HTML.** Edit `curriculum/units/*.json`, then:
```bash
python3 tools/validate.py && python3 tools/build_docs.py
```
No Node in this environment — tooling is Python 3 (stdlib only, no install step).
`docs/brooklyn-curriculum.html` is build output; never hand-edit it.

## Status
- Approach chosen: **curriculum first**, before building software.
- **All 12 units authored** → `curriculum/units/`. 48 objective cards, 144 leveled variants.
  Each unit carries a domain × level can-do matrix with a scaffold and a check per cell, plus target
  structures, core/academic vocabulary, a foundational-literacy strand, a teaching note, and a worked
  task at all three levels. Validated clean by `tools/validate.py`.
- **Curriculum reference generated** → `docs/brooklyn-curriculum.html`. Verified in-browser
  2026-07-20: 12 units, 48 domain rows, 144 leveled cells, 36 worked-task cards, both color schemes,
  no page-level horizontal overflow (wide tables scroll inside their own container).
- **Objective Card prototype done and verified** → `prototypes/brooklyn-objective-card.html`.
  One source card rendering to both print packet and device task. Verified in-browser 2026-07-20:
  level switch (L1/L2/L3) and surface switch (device/print) both work and compose correctly; no
  console errors. Fixed a malformed CSS rule (a selector list ran into an `@media` block) that was
  dropping the dark-mode pressed-chip color.

## Known duplication (worth fixing before the content grows)
`docs/brooklyn-scope-and-sequence.html` is the hand-designed **pitch** doc. It still hand-codes the
12-unit grid and the Unit 01 exemplar in HTML, so that content now exists in two places — there and in
`curriculum/units/`. Edit the JSON and the pitch doc silently goes stale. Fix by having
`build_docs.py` emit those two sections as fragments injected between marker comments.

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
