#!/usr/bin/env python3
"""Validate every Brooklyn unit against the Objective Card schema.

Run: python3 tools/validate.py
Exits non-zero if anything is wrong, so it can gate a commit.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
UNITS_DIR = ROOT / "curriculum" / "units"

DOMAINS = ["Listening", "Speaking", "Reading", "Writing"]
MODE_FOR = {"Listening": "Interpretive", "Reading": "Interpretive",
            "Speaking": "Expressive", "Writing": "Expressive"}
LEVELS = ["1", "2", "3"]
PHASES = ["A", "B", "C"]
WIDA_STANDARDS = ["SI", "LA", "MA", "SC", "SS"]
KEY_USES = ["Narrate", "Inform", "Explain", "Argue"]

errors = []
warnings = []


def err(unit, msg):
    errors.append(f"u{unit}: {msg}")


def warn(unit, msg):
    warnings.append(f"u{unit}: {msg}")


def check_unit(path):
    try:
        unit = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"{path.name}: invalid JSON — {e}")
        return None

    no = unit.get("no", path.stem)

    # --- required top-level fields
    for field in ["no", "title", "phase", "weeks", "focus", "standards", "function",
                  "grammar", "vocabulary", "foundationalLiteracy", "cards", "workedTask"]:
        if field not in unit:
            err(no, f"missing required field '{field}'")

    if unit.get("no") != path.stem[1:]:
        err(no, f"'no' ({unit.get('no')}) does not match filename {path.name}")
    if unit.get("phase") not in PHASES:
        err(no, f"phase must be one of {PHASES}, got {unit.get('phase')!r}")

    # --- standards
    if "wida" in unit:
        err(no, "`wida` must live under `standards.wida` (run tools/migrate_standards_l1.py)")
    wida = unit.get("standards", {}).get("wida", {})
    for std in wida.get("standards", []):
        if std not in WIDA_STANDARDS:
            err(no, f"unknown WIDA standard {std!r}")
    if not wida.get("standards"):
        err(no, "wida.standards is empty")
    for ku in wida.get("keyUses", []):
        if ku not in KEY_USES:
            err(no, f"unknown Key Use {ku!r} (expected one of {KEY_USES})")
    if not wida.get("keyUses"):
        err(no, "wida.keyUses is empty")

    # --- vocabulary
    vocab = unit.get("vocabulary", {})
    for bucket in ["core", "academic"]:
        if not vocab.get(bucket):
            err(no, f"vocabulary.{bucket} is empty")

    # --- cards: exactly four, one per domain, correct mode, all three levels
    cards = unit.get("cards", [])
    seen = [c.get("domain") for c in cards]
    if seen != DOMAINS:
        err(no, f"cards must be exactly {DOMAINS} in order, got {seen}")

    for card in cards:
        domain = card.get("domain", "?")
        expected_id = f"u{unit.get('no')}-{domain.lower()}"
        if card.get("id") != expected_id:
            err(no, f"card id should be {expected_id!r}, got {card.get('id')!r}")
        if card.get("mode") != MODE_FOR.get(domain):
            err(no, f"{domain} mode should be {MODE_FOR.get(domain)!r}, got {card.get('mode')!r}")

        levels = card.get("levels", {})
        if sorted(levels.keys()) != LEVELS:
            err(no, f"{domain} must have levels {LEVELS}, got {sorted(levels.keys())}")
        for lv in LEVELS:
            spec = levels.get(lv, {})
            for field in ["canDo", "scaffold", "check", "l1Bridge"]:
                if not spec.get(field, "").strip():
                    err(no, f"{domain} L{lv} missing '{field}'")

    # --- worked task
    wt = unit.get("workedTask", {})
    if wt.get("domain") not in DOMAINS:
        err(no, f"workedTask.domain invalid: {wt.get('domain')!r}")
    if not wt.get("prompt", "").strip():
        err(no, "workedTask missing 'prompt'")
    wt_levels = wt.get("levels", {})
    if sorted(wt_levels.keys()) != LEVELS:
        err(no, f"workedTask must have levels {LEVELS}, got {sorted(wt_levels.keys())}")
    for lv in LEVELS:
        spec = wt_levels.get(lv, {})
        for field in ["say", "scaffold"]:
            if not spec.get(field, "").strip():
                err(no, f"workedTask L{lv} missing '{field}'")
        # every [slot] must be non-empty and lowercase-ish, and L1 should be simplest
        for slot in re.findall(r"\[([^\]]*)\]", spec.get("say", "")):
            if not slot.strip():
                err(no, f"workedTask L{lv} has an empty [] slot")

    # --- pedagogical progression, measured on actual student output.
    # Deliberately NOT measured on can-do text: a simpler task often takes more
    # words to describe ("recognize my own name with picture support" is longer
    # than, and easier than, "read a peer profile"). The worked task's `say` is
    # the real signal — it is literally what the student produces.
    says = [wt_levels.get(lv, {}).get("say", "") for lv in LEVELS]
    if not (len(says[0]) < len(says[1]) < len(says[2])):
        warn(no, "worked-task output does not grow L1 < L2 < L3 — check the progression")

    return unit


def check_prototype(units):
    """The prototype hardcodes its own copy of the u01 Speaking card, because a
    file:// page cannot fetch the JSON. That copy drifted from the curriculum
    once already, so verify it still agrees. Delete this check once the
    prototype's card is generated at build time.
    """
    proto = ROOT / "prototypes" / "brooklyn-objective-card.html"
    if not proto.exists():
        return
    src = proto.read_text()
    u01 = next((u for u in units if u.get("no") == "01"), None)
    if not u01:
        return
    speaking = next((c for c in u01["cards"] if c["domain"] == "Speaking"), None)
    if not speaking:
        return

    m = re.search(r'id:"([^"]+)"', src)
    if m and m.group(1) != speaking["id"]:
        errors.append(f"prototype: card id {m.group(1)!r} != curriculum {speaking['id']!r}")

    m = re.search(r'fn:"([^"]+)"', src)
    if m and m.group(1) != u01["function"]:
        errors.append(f"prototype: function drifted from curriculum u01")

    for i, lv in enumerate(LEVELS):
        found = re.findall(r'canDo:"([^"]+)"', src)
        if i < len(found):
            want = speaking["levels"][lv]["canDo"]
            if found[i] != want:
                errors.append(
                    f"prototype: L{lv} can-do drifted from curriculum\n"
                    f"          prototype:  {found[i]}\n"
                    f"          curriculum: {want}")


def main():
    paths = sorted(UNITS_DIR.glob("u*.json"))
    if not paths:
        print(f"No unit files found in {UNITS_DIR}", file=sys.stderr)
        return 1

    units = [u for u in (check_unit(p) for p in paths) if u]

    # --- sequence-level checks
    numbers = [u.get("no") for u in units]
    expected = [f"{i:02d}" for i in range(1, len(units) + 1)]
    if numbers != expected:
        errors.append(f"unit numbers not contiguous: {numbers}")

    check_prototype(units)

    ids = [c["id"] for u in units for c in u.get("cards", []) if "id" in c]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errors.append(f"duplicate card ids: {sorted(dupes)}")

    print(f"Checked {len(units)} units, {len(ids)} objective cards "
          f"({len(ids) * 3} level variants).\n")

    for w in warnings:
        print(f"  warn  {w}")
    for e in errors:
        print(f"  ERROR {e}")

    if errors:
        print(f"\n{len(errors)} error(s).")
        return 1
    print(f"All units valid.{'' if not warnings else f' ({len(warnings)} warning(s).)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
