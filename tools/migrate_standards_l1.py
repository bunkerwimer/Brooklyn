#!/usr/bin/env python3
"""One-shot migration: nest `wida` under `standards`, and add the L1 bridge.

Run once: python3 tools/migrate_standards_l1.py
Idempotent — safe to re-run.

Why the L1 bridge exists: the target learner is highly multilingual and often SLIFE.
CLAUDE.md promised a language-agnostic home-language "bridge" slot from the start; it
was never actually in the schema. This adds it to all 144 level variants.

Design principle — the bridge FADES but never disappears:
  L1  home language carries meaning; English is echoed
  L2  home language previews and rehearses; English is produced
  L3  home language is for planning and thinking; English is the product
Two deliberate exceptions where the bridge does NOT fade, because comprehension
outranks language practice: safety/health information, and anything a family must
act on (graduation requirements, medical instructions).
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
UNITS = ROOT / "curriculum" / "units"

L1B = {
 "01": {
  "Listening": ["Preview hello, name, and from in the home language; pointing to the photo is a full answer.",
                "Give country and language names in the home language first, then English, so only the frame is new.",
                "Note-catcher may be annotated in the home language; the matching task stays in English."],
  "Speaking":  ["Student may greet in the home language first, then echo the English model. Both count.",
                "Rehearse the three-slot frame silently in the home language before producing it in English.",
                "Plan the reciprocal question in the home language; deliver it in English."],
  "Reading":   ["If the home language uses a different script, show the student's own name in both.",
                "ID-card field labels (name, country, language) glossed in the home language.",
                "Home-language glossary for the three profiles; the matching is done in English."],
  "Writing":   ["Where the home script differs, practice the Latin-alphabet form alongside the original.",
                "Form labels glossed in the home language; the student writes in English.",
                "Draft one sentence in the home language, then write all three in English."]},
 "02": {
  "Listening": ["Building photos labeled in the home language on first exposure only.",
                "Direction words pre-taught in the home language before the map task.",
                "Note-catcher headings glossed; the announcement stays in English."],
  "Speaking":  ["Student may name the place in the home language while showing the pass card; teacher supplies the English.",
                "Rehearse 'Where is the ___?' after hearing the equivalent question in the home language.",
                "Plan the route in the home language, give the directions in English."],
  "Reading":   ["Pair each real sign photo with its home-language meaning once, then remove the gloss.",
                "Schedule column headers (period, room, teacher) glossed in the home language.",
                "Staff role names glossed — job titles rarely transfer directly between school systems."],
  "Writing":   ["Room numbers are language-neutral; start here to build early success.",
                "Map word bank shown bilingually; labels written in English.",
                "Draft the note in the home language if needed, then write the English version."]},
 "03": {
  "Listening": ["Demonstrate each command physically; confirm meaning in the home language once, then drop it.",
                "Question words (what/where/who/when) glossed in the home language on the poster.",
                "Student may take notes in the home language while following English directions."],
  "Speaking":  ["Help card printed in both languages so the student can signal without speaking English.",
                "State explicitly, in the home language, that asking a teacher to repeat is polite here.",
                "Formulate the clarifying question in the home language, ask it in English."],
  "Reading":   ["Direction verbs paired with icons and a one-time home-language gloss.",
                "Worksheet direction verbs glossed in the margin.",
                "Assignment terms (due, submit, draft) glossed — several are false friends."],
  "Writing":   ["Heading fields (name, date, page) labeled bilingually on the template.",
                "Student may write the question in the home language first, then translate with support.",
                "Drafting in the home language is permitted; the message is submitted in English."]},
 "04": {
  "Listening": ["Check which numbers the student already holds in the home language before teaching English ones.",
                "State explicitly, in the home language, that US clocks use 12-hour time with a.m./p.m.",
                "Note-catcher headings glossed; the announcement stays in English."],
  "Speaking":  ["Counting may be rehearsed in the home language first to confirm number sense, then in English.",
                "Subject names glossed in the home language on the schedule.",
                "Reason about the scheduling conflict in the home language, explain it in English."],
  "Reading":   ["Day and month names glossed once; numerals need no translation.",
                "Schedule headings glossed in the home language.",
                "Calendar legend terms (early release, no school) glossed — these are district-specific."],
  "Writing":   ["Explicitly contrast US month/day/year order with the student's home format, in the home language.",
                "Subject word bank shown bilingually.",
                "Plan the week in the home language, write it in English."]},
 "05": {
  "Listening": ["Body-part and feeling words glossed in the home language; pointing is always sufficient.",
                "Preview the nurse's questions in the home language so the student knows what will be asked.",
                "Follow-up questions about duration and severity glossed in advance."],
  "Speaking":  ["Student may name the symptom in the home language. Getting help outranks producing English.",
                "Frame rehearsed after hearing the equivalent in the home language.",
                "A distressed student may describe the symptom in the home language first, then in English."],
  "Reading":   ["Safety signs glossed in the home language and NOT faded — this is a safety skill, not a language test.",
                "Form field labels glossed in the home language.",
                "Care instructions provided bilingually; the trigger condition is identified in English."],
  "Writing":   ["Check-in slip printed bilingually.",
                "Symptom word bank shown bilingually.",
                "Absence note may be drafted in the home language and finalized in English with support."]},
 "06": {
  "Listening": ["Kinship terms glossed carefully — they rarely map one-to-one between languages.",
                "Descriptive adjectives glossed before the photo task.",
                "Relationship web may be annotated in the home language."],
  "Speaking":  ["Student may use the home-language kinship term; teacher supplies the nearest English word and names the mismatch.",
                "Adjective bank shown bilingually.",
                "Plan the description in the home language, deliver it in English including the question back."],
  "Reading":   ["Family word-picture cards glossed once.",
                "Passage vocabulary glossed in the margin.",
                "Inference prompt given in the home language; evidence is cited from the English text."],
  "Writing":   ["Word bank shown bilingually.",
                "Student may draft in the home language; final sentences in English.",
                "Organizer headings glossed; the paragraph is written in English."]},
 "07": {
  "Listening": ["Use photos of the actual serving line — food is largely language-neutral when shown.",
                "Serving-line questions previewed in the home language.",
                "Ingredient terms glossed precisely; dietary-restriction vocabulary must be exact."],
  "Speaking":  ["Pocket card printed bilingually so the student can order without speaking English.",
                "Polite request frame rehearsed after the home-language equivalent.",
                "Rehearse the restriction in the home language first. Accuracy matters more than fluency here."],
  "Reading":   ["Menu items glossed once alongside photos.",
                "Menu category headings glossed in the home language.",
                "Allergen and ingredient terms provided bilingually and NOT faded — this is a safety translation."],
  "Writing":   ["Like / don't like columns labeled bilingually.",
                "Food word bank shown bilingually.",
                "The home-country meal may be drafted in the home language; the student is the expert and should not be capped by English."]},
 "08": {
  "Listening": ["Place words glossed; direction arrows are language-neutral.",
                "Direction vocabulary pre-taught in the home language.",
                "Transit announcement note-catcher headings glossed."],
  "Speaking":  ["Wallet card printed bilingually with address and emergency contact. This is a safety artifact, not a worksheet.",
                "Frame rehearsed after the home-language equivalent.",
                "Plan the directions in the home language, give them in English."],
  "Reading":   ["Community and safety signs glossed and NOT faded — over-scaffold safety, never under.",
                "Transit schedule key glossed in the home language.",
                "Resource flyers provided in the home language wherever the district has translations."],
  "Writing":   ["Address order differs by country; show the US order explicitly in the home language.",
                "Place word bank shown bilingually.",
                "Sequence the directions in the home language, write them in English."]},
 "09": {
  "Listening": ["Routine verbs glossed alongside action photos.",
                "Sequence words glossed before the ordering task.",
                "Frequency adverbs glossed — they rarely map cleanly and are a persistent error source."],
  "Speaking":  ["Student may name the action in the home language; teacher supplies the English verb.",
                "Sequence frame rehearsed after the home-language equivalent.",
                "Plan the usual-versus-exception contrast in the home language, deliver it in English."],
  "Reading":   ["Verb-picture cards glossed once.",
                "Passage vocabulary glossed in the margin.",
                "Comparison sentence starters glossed; the comparison is written in English."],
  "Writing":   ["Timeline word bank shown bilingually.",
                "Sequence-word bank shown bilingually.",
                "Draft the paragraph in the home language if needed; final version in English."]},
 "10": {
  "Listening": ["Adjectives glossed with paired objects; teach opposites together.",
                "Explain comparison structure in the home language — languages mark comparison very differently.",
                "Ranking organizer headings glossed."],
  "Speaking":  ["Student may give the adjective in the home language; teacher supplies the English.",
                "Explicitly contrast how the home language forms comparatives with English -er / more.",
                "Justify the choice in the home language first, then in English with because."],
  "Reading":   ["Adjective-picture cards glossed once.",
                "Description vocabulary glossed.",
                "Criteria table headings glossed; the table is completed in English."],
  "Writing":   ["Adjective word bank shown bilingually.",
                "Mark the -er / more split explicitly against the home-language pattern.",
                "Plan the comparison in the home language, write it in English."]},
 "11": {
  "Listening": ["Explain the now / before sort in the home language — past marking varies enormously across languages.",
                "Story events previewed in the home language before the ordering task.",
                "Timeline may be annotated in the home language."],
  "Speaking":  ["Student may tell the event in the home language first; teacher supplies the English past form. Never require English for a personal story.",
                "Rehearse the sequence in the home language, deliver in English. The topic stays the student's choice.",
                "The student may narrate in the home language and then retell in English, or decline. Both are full credit."],
  "Reading":   ["Present/past verb pairs glossed once.",
                "Narrative vocabulary glossed in the margin.",
                "Offer published newcomer narratives in the home language where they exist."],
  "Writing":   ["Past-verb word bank shown bilingually.",
                "Drafting in the home language is permitted; final version in English.",
                "The student may write the narrative in the home language and translate with support. The language of the first draft is never the point."]},
 "12": {
  "Listening": ["Explain the now / later sort in the home language.",
                "Goal and reason vocabulary glossed.",
                "The counselor's explanation should be INTERPRETED, not glossed — graduation requirements are too consequential to approximate."],
  "Speaking":  ["Student may state the goal in the home language; teacher supplies the English.",
                "Rehearse the because frame after the home-language equivalent.",
                "Plan the request in the home language; hold any conversation about credits with an interpreter present."],
  "Reading":   ["Goal words glossed once.",
                "Profile vocabulary glossed.",
                "Graduation requirements MUST be provided in the home language. Never make a student parse their own transcript in a new language."],
  "Writing":   ["Goal word bank shown bilingually.",
                "Drafting in the home language is permitted.",
                "The plan may be drafted in the home language. The English copy is for the counselor; the family copy should be in the home language."]},
}


def main():
    changed = 0
    for path in sorted(UNITS.glob("u*.json")):
        unit = json.loads(path.read_text())
        no = unit["no"]

        # 1. nest wida under standards (idempotent)
        if "wida" in unit and "standards" not in unit:
            wida = unit.pop("wida")
            rebuilt = {}
            for k, v in unit.items():
                rebuilt[k] = v
                if k == "focus":
                    rebuilt["standards"] = {"wida": wida}
            unit = rebuilt

        # 2. add l1Bridge to every level variant
        for card in unit["cards"]:
            bridges = L1B[no][card["domain"]]
            for i, lv in enumerate(["1", "2", "3"]):
                card["levels"][lv]["l1Bridge"] = bridges[i]

        path.write_text(json.dumps(unit, indent=2, ensure_ascii=False) + "\n")
        changed += 1

    print(f"Migrated {changed} units: standards nested, l1Bridge added to "
          f"{changed * 4 * 3} level variants.")


if __name__ == "__main__":
    main()
