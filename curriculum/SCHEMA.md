# Brooklyn — Objective Card schema

One authored object is the unit of everything. A **unit** holds four **objective cards** (one per
language domain), and each card holds three **level variants**. Everything the platform renders —
print packet, projector routine, device task, small-group cards — compiles from these files.

Source of truth: `curriculum/units/u01.json` … `u12.json`. Nothing should hand-author unit content
in HTML; the docs are generated (`npm run build:docs` → `node tools/build-docs.mjs`).

## Unit

```jsonc
{
  "no": "01",                    // string, zero-padded — used in IDs and print headers
  "title": "Hello & Who I Am",
  "phase": "A",                  // A = Orientation & Survival, B = Daily Life, C = Expanding Language
  "weeks": "1–2",
  "focus": "One-line description shown in the scope & sequence.",
  "standards": {
    "wida": {
      "standards": ["SI"],       // SI, LA, MA, SC, SS — WIDA ELD Standards (2020)
      "keyUses": ["Inform"]      // Narrate, Inform, Explain, Argue
    }
    // Other frameworks (CA ELD, TX ELPS, NY) are NOT tagged per unit. They are
    // derived at render time from curriculum/standards/frameworks.json, so a unit
    // is authored once and mapped many times. See "Standards coverage" below.
  },
  "function": "The language function the unit is built around.",
  "grammar": ["Target structure 1", "Target structure 2"],
  "vocabulary": {
    "core": ["…"],               // high-frequency survival words, taught to automaticity
    "academic": ["…"]            // cross-content terms that transfer to mainstream classes
  },
  "foundationalLiteracy": "The decoding/print strand for this unit — runs parallel for SLIFE learners.",
  "culturalNote": "What to be careful about with newcomers. Optional but strongly encouraged.",
  "cards": [ /* four Cards — Listening, Speaking, Reading, Writing */ ],
  "workedTask": { /* one domain rendered at all three levels — the personalization demo */ }
}
```

## Card

```jsonc
{
  "id": "u01-speaking",          // `u{no}-{domain}` — stable, referenced by the renderer
  "domain": "Speaking",          // Listening | Speaking | Reading | Writing
  "mode": "Expressive",          // Interpretive (L, R) | Expressive (S, W)
  "levels": {
    "1": {                       // WIDA 1 Entering / 2 Emerging / 3 Developing
      "canDo": "The observable target. This is what a teacher looks for.",
      "scaffold": "The support that makes it reachable at this level.",
      "l1Bridge": "How the home language carries meaning at this level.",
      "check": "The evidence a teacher records."
    },
    "2": { … }, "3": { … }
  }
}
```

**`canDo`** is the contract with the district — it maps to a WIDA Can-Do descriptor and is what
appears on a report. **`scaffold`** is what the print packet and device task actually build.
**`check`** is what a teacher records; write it so it can be scored in seconds.

**`check` is formative, not psychometric.** It is evidence a teacher observed something, not a
measurement of proficiency-level movement. Level movement is measured by the state summative
(ACCESS, ELPAC, TELPAS, NYSESLAT). Never describe these as level-movement data to a district
without validity and reliability evidence, which does not exist yet.

**`l1Bridge`** is the home-language support, written to be **language-agnostic** — it names a
mechanism ("gloss the field labels", "rehearse in the home language, produce in English"), never a
specific language, so it works for a highly multilingual roster. It **fades** across levels:

- **L1** home language carries meaning; English is echoed
- **L2** home language previews and rehearses; English is produced
- **L3** home language is for planning and thinking; English is the product

Two deliberate exceptions where the bridge does **not** fade, because comprehension outranks
language practice: **safety and health information**, and **anything a family must act on**
(graduation requirements, medical instructions, legal rights).

## Worked task

The personalization demo: one objective served three ways, showing that levels differ in *support*,
not in *topic*. Every student is doing the same lesson.

```jsonc
{
  "domain": "Speaking",
  "levels": {
    "1": { "say": "Hello. I am [name].", "scaffold": "Word bank + photo cards…" },
    "2": { … }, "3": { … }
  }
}
```

Bracketed `[slots]` are the blanks the renderer turns into chips (device) or write-on lines (print).

## Level design rules

Applied consistently across all twelve units:

- **L1 Entering** — single words, formulaic chunks, gesture and pointing. Recognition over production.
  Never requires writing beyond copying. Always has a non-verbal way to show understanding.
- **L2 Emerging** — sentence frames with 2–3 slots. Produces from a model.
- **L3 Developing** — open frames, connected sentences, and **initiating** (asking back, extending,
  explaining a choice). This is where academic language starts.

Levels change the **scaffold**, never the **content**. A newcomer at L1 and a peer at L3 are in the
same conversation — this is the pedagogical claim the whole product rests on.

## Standards coverage

WIDA is the primary framework, but it is roughly 40 states and — critically — **not** California,
Texas, New York, or Arizona, which together hold a large share of the nation's English learners.
`curriculum/standards/frameworks.json` holds framework metadata plus a level and domain crosswalk
so one authored objective can be reported against several frameworks.

**The crosswalk is unvalidated.** No official equivalence exists between these frameworks; they
define proficiency on different constructs. Domain mapping is high confidence, level mapping is not,
and expectation-code-level mapping is deliberately **absent rather than guessed**. A credentialed
reviewer holding each state's current documents must validate it before the curriculum is shown to
a district in that state. The generated doc prints this caveat on the page.

## Standards note

Independent alignment to the WIDA ELD Standards Framework (2020). Not affiliated with, authorized by,
or endorsed by WIDA / the University of Wisconsin.
