#!/usr/bin/env python3
"""Generate the Brooklyn curriculum reference from the unit data.

Run: python3 tools/build_docs.py
Writes: docs/brooklyn-curriculum.html

The docs are BUILD OUTPUT. Never hand-edit the generated file — edit the JSON in
curriculum/units/ and re-run this.
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
UNITS_DIR = ROOT / "curriculum" / "units"
OUT = ROOT / "docs" / "brooklyn-curriculum.html"

LEVELS = [("1", "Entering"), ("2", "Emerging"), ("3", "Developing")]
PHASE_NAMES = {
    "A": ("Orientation &amp; Survival", "Weeks 1&ndash;8"),
    "B": ("Daily Life &amp; Community", "Weeks 9&ndash;16"),
    "C": ("Expanding Language", "Weeks 17&ndash;24"),
}
STANDARD_NAMES = {
    "SI": "Social &amp; Instructional", "LA": "Language Arts",
    "MA": "Mathematics", "SC": "Science", "SS": "Social Studies",
}


def e(s):
    return html.escape(str(s), quote=False)


def slots(text):
    """Render [slot] placeholders as styled blanks."""
    return re.sub(r"\[([^\]]+)\]",
                  lambda m: f'<span class="blank">{e(m.group(1))}</span>',
                  e(text))


STYLE = """
  :root {
    --paper:#F4F6F5; --surface:#FFFFFF; --surface-2:#ECF0EE;
    --ink:#17242A; --ink-2:#4B5E64; --ink-3:#7C8D91;
    --line:#D9E1DE; --line-2:#E7ECEA;
    --accent:#1E6E63; --accent-ink:#124039; --accent-tint:#E1EEEA;
    --warm:#B6611F; --warm-tint:#F3E6D6;
    --lvl1-bg:#E3F1ED; --lvl2-bg:#D2E9E2; --lvl3-bg:#C3E0D7;
    --lvl1-fg:#2C6A5E; --lvl2-fg:#1F6255; --lvl3-fg:#154B41;
    --shadow:0 1px 2px rgba(20,45,40,.05), 0 8px 24px -12px rgba(20,45,40,.18);
    --radius:14px;
    --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --serif:Georgia,"Iowan Old Style","Times New Roman",serif;
    --mono:ui-monospace,SFMono-Regular,Menlo,"Cascadia Mono",Consolas,monospace;
  }
  @media (prefers-color-scheme: dark) { :root { __DARK__ } }
  :root[data-theme="light"] { __LIGHT__ }
  :root[data-theme="dark"] { __DARK__ }

  * { box-sizing:border-box; }
  body { margin:0; }
  .page { background:var(--paper); color:var(--ink); font-family:var(--sans);
          font-size:16px; line-height:1.6; -webkit-font-smoothing:antialiased;
          padding:clamp(20px,5vw,64px) clamp(16px,5vw,48px) 80px; }
  .wrap { max-width:1080px; margin:0 auto; }
  h1,h2,h3,h4 { margin:0; line-height:1.15; text-wrap:balance; letter-spacing:-.01em; }
  p { margin:0; }
  a { color:var(--accent); }

  .eyebrow { font-family:var(--mono); font-size:12px; letter-spacing:.16em;
             text-transform:uppercase; color:var(--accent); font-weight:600; }
  .hero { margin-bottom:44px; }
  .hero h1 { font-size:clamp(30px,5.2vw,46px); margin:10px 0 14px; }
  .lede { color:var(--ink-2); font-size:clamp(16px,2.1vw,19px); max-width:64ch; }
  .metastrip { display:flex; flex-wrap:wrap; gap:8px; margin-top:20px; }
  .chip { font-family:var(--mono); font-size:12.5px; border:1px solid var(--line);
          background:var(--surface); border-radius:999px; padding:6px 12px; color:var(--ink-2); }
  .chip b { color:var(--ink); font-weight:600; }

  /* contents */
  .toc { background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
         padding:22px 24px; margin-bottom:52px; box-shadow:var(--shadow); }
  .toc h2 { font-size:15px; font-family:var(--mono); letter-spacing:.1em;
            text-transform:uppercase; color:var(--ink-3); margin-bottom:14px; font-weight:600; }
  .toc ol { margin:0; padding:0; list-style:none; display:grid;
            grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:2px 20px; }
  .toc li { border-bottom:1px solid var(--line-2); }
  .toc a { display:flex; gap:10px; padding:7px 2px; text-decoration:none; color:var(--ink); }
  .toc a:hover { color:var(--accent); }
  .toc .n { font-family:var(--mono); color:var(--ink-3); font-size:13px; }

  /* phase */
  .phase-head { display:flex; align-items:baseline; gap:14px; flex-wrap:wrap;
                margin:56px 0 20px; padding-bottom:12px; border-bottom:2px solid var(--accent); }
  .phase-head .ph { font-family:var(--mono); font-size:12px; letter-spacing:.14em;
                    text-transform:uppercase; background:var(--accent-tint); color:var(--accent-ink);
                    padding:4px 10px; border-radius:999px; font-weight:600; }
  .phase-head h2 { font-size:clamp(21px,3.2vw,27px); }
  .phase-head .wk { margin-left:auto; color:var(--ink-3); font-family:var(--mono); font-size:12.5px; }

  /* unit */
  .unit { background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
          box-shadow:var(--shadow); padding:clamp(20px,3vw,32px); margin-bottom:28px;
          scroll-margin-top:20px; }
  .unit-head { border-bottom:1px solid var(--line-2); padding-bottom:18px; margin-bottom:20px; }
  .unit-no { font-family:var(--mono); font-size:13px; color:var(--accent);
             letter-spacing:.1em; font-weight:600; }
  .unit-head h3 { font-size:clamp(21px,3vw,28px); margin:6px 0 8px; }
  .unit-head .focus { color:var(--ink-2); max-width:70ch; }
  .fn { font-family:var(--serif); font-size:17px; color:var(--ink);
        background:var(--accent-tint); border-left:3px solid var(--accent);
        padding:12px 16px; border-radius:0 8px 8px 0; margin-top:16px; }

  .grid2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:18px; margin:20px 0; }
  .box { background:var(--surface-2); border-radius:10px; padding:14px 16px; }
  .box h4 { font-family:var(--mono); font-size:11.5px; letter-spacing:.12em;
            text-transform:uppercase; color:var(--ink-3); margin-bottom:8px; font-weight:600; }
  .box ul { margin:0; padding-left:18px; color:var(--ink-2); font-size:14.5px; }
  .box li { margin-bottom:3px; }
  .words { display:flex; flex-wrap:wrap; gap:5px; }
  .w { font-size:13px; background:var(--surface); border:1px solid var(--line);
       border-radius:6px; padding:2px 8px; color:var(--ink-2); }
  .w.acad { border-color:var(--accent); color:var(--accent-ink); background:var(--accent-tint); }

  .note { border:1px solid var(--warm); background:var(--warm-tint); border-radius:10px;
          padding:14px 16px; margin:20px 0; }
  .note h4 { font-family:var(--mono); font-size:11.5px; letter-spacing:.12em; text-transform:uppercase;
             color:var(--warm); margin-bottom:6px; font-weight:700; }
  .note p { font-size:14.5px; color:var(--ink); }

  /* matrix */
  .scroll-x { overflow-x:auto; margin:22px 0; }
  table.matrix { border-collapse:separate; border-spacing:0; width:100%; min-width:720px; font-size:14px; }
  table.matrix th, table.matrix td { text-align:left; vertical-align:top; padding:12px 14px;
                                     border-bottom:1px solid var(--line-2); }
  table.matrix thead th { font-family:var(--mono); font-size:11.5px; letter-spacing:.1em;
                          text-transform:uppercase; color:var(--ink-3); border-bottom:1px solid var(--line);
                          white-space:nowrap; }
  td.rowhead, th.rowhead { font-weight:600; white-space:nowrap; width:120px; }
  td.rowhead small { display:block; font-weight:400; color:var(--ink-3);
                     font-size:11.5px; letter-spacing:.04em; }
  .c1 { background:var(--lvl1-bg); } .c2 { background:var(--lvl2-bg); } .c3 { background:var(--lvl3-bg); }
  .c1, .c2, .c3 { color:var(--ink); }
  .cando { display:block; margin-bottom:7px; }
  .sub { display:block; font-size:12.5px; color:var(--ink-2); padding-top:6px;
         border-top:1px dotted rgba(0,0,0,.14); }
  :root[data-theme="dark"] .sub { border-top-color:rgba(255,255,255,.16); }
  @media (prefers-color-scheme:dark) { .sub { border-top-color:rgba(255,255,255,.16); } }
  .sub b { font-family:var(--mono); font-size:10.5px; letter-spacing:.09em;
           text-transform:uppercase; opacity:.75; }

  /* worked task */
  .worked { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; margin-top:14px; }
  .wcard { border:1px solid var(--line); border-radius:12px; overflow:hidden; background:var(--surface); }
  .wtop { padding:9px 14px; font-size:13px; font-weight:700; display:flex; gap:8px; align-items:center; }
  .wtop.t1 { background:var(--lvl1-bg); color:var(--lvl1-fg); }
  .wtop.t2 { background:var(--lvl2-bg); color:var(--lvl2-fg); }
  .wtop.t3 { background:var(--lvl3-bg); color:var(--lvl3-fg); }
  .wbody { padding:14px; }
  .say { font-family:var(--serif); font-size:16px; line-height:1.5; margin-bottom:10px; }
  .blank { background:var(--warm-tint); color:var(--warm); border-bottom:1.5px solid var(--warm);
           padding:0 5px; border-radius:3px 3px 0 0; font-style:italic; }
  .scaffold { font-size:13px; color:var(--ink-2); }
  .sl { font-family:var(--mono); font-size:10.5px; letter-spacing:.09em; text-transform:uppercase;
        color:var(--ink-3); display:block; margin-bottom:3px; }

  footer.legal { margin-top:56px; padding-top:22px; border-top:1px solid var(--line);
                 color:var(--ink-3); font-size:12px; line-height:1.7; text-align:center; }

  @media print {
    .page { padding:0; background:#fff; }
    .toc { break-after:page; }
    .unit { break-inside:avoid; box-shadow:none; }
    .phase-head { break-before:page; }
  }
"""

LIGHT = """--paper:#F4F6F5; --surface:#FFFFFF; --surface-2:#ECF0EE;
    --ink:#17242A; --ink-2:#4B5E64; --ink-3:#7C8D91;
    --line:#D9E1DE; --line-2:#E7ECEA;
    --accent:#1E6E63; --accent-ink:#124039; --accent-tint:#E1EEEA;
    --warm:#B6611F; --warm-tint:#F3E6D6;
    --lvl1-bg:#E3F1ED; --lvl2-bg:#D2E9E2; --lvl3-bg:#C3E0D7;
    --lvl1-fg:#2C6A5E; --lvl2-fg:#1F6255; --lvl3-fg:#154B41;
    --shadow:0 1px 2px rgba(20,45,40,.05), 0 8px 24px -12px rgba(20,45,40,.18);"""

DARK = """--paper:#0E181C; --surface:#14232A; --surface-2:#1B2E36;
    --ink:#E8EFEC; --ink-2:#A6BAB7; --ink-3:#70878A;
    --line:#26383F; --line-2:#203138;
    --accent:#5BC6B4; --accent-ink:#AEE3D8; --accent-tint:#173A38;
    --warm:#E0925A; --warm-tint:#33241A;
    --lvl1-bg:#183531; --lvl2-bg:#1B4B43; --lvl3-bg:#215E53;
    --lvl1-fg:#A9D8CE; --lvl2-fg:#B9E5DB; --lvl3-fg:#CFEFE7;
    --shadow:0 1px 2px rgba(0,0,0,.3), 0 10px 30px -14px rgba(0,0,0,.6);"""


def render_unit(u):
    out = []
    a = out.append
    no, title = e(u["no"]), e(u["title"])
    a(f'<article class="unit" id="u{no}">')
    a('  <div class="unit-head">')
    a(f'    <div class="unit-no">Unit {no} &middot; {e(u["weeks"])}</div>')
    a(f'    <h3>{title}</h3>')
    a(f'    <p class="focus">{e(u["focus"])}</p>')

    stds = " &middot; ".join(f'{s} {STANDARD_NAMES.get(s, "")}'.strip()
                             for s in u["wida"]["standards"])
    kus = ", ".join(e(k) for k in u["wida"]["keyUses"])
    a('    <div class="metastrip">')
    a(f'      <span class="chip"><b>WIDA</b> {stds}</span>')
    a(f'      <span class="chip"><b>Key Use</b> {kus}</span>')
    a('    </div>')
    a(f'    <p class="fn">{e(u["function"])}</p>')
    a('  </div>')

    # grammar + literacy
    a('  <div class="grid2">')
    a('    <div class="box"><h4>Target structures</h4><ul>')
    for g in u["grammar"]:
        a(f'      <li>{e(g)}</li>')
    a('    </ul></div>')
    a('    <div class="box"><h4>Foundational literacy strand</h4>'
      f'<p style="font-size:14.5px;color:var(--ink-2)">{e(u["foundationalLiteracy"])}</p></div>')
    a('  </div>')

    # vocabulary
    a('  <div class="box" style="margin-bottom:4px"><h4>Vocabulary &mdash; core</h4><div class="words">')
    for w in u["vocabulary"]["core"]:
        a(f'    <span class="w">{e(w)}</span>')
    a('  </div></div>')
    a('  <div class="box"><h4>Vocabulary &mdash; academic</h4><div class="words">')
    for w in u["vocabulary"]["academic"]:
        a(f'    <span class="w acad">{e(w)}</span>')
    a('  </div></div>')

    if u.get("culturalNote"):
        a('  <div class="note"><h4>Teaching note</h4>'
          f'<p>{e(u["culturalNote"])}</p></div>')

    # matrix
    a('  <div class="scroll-x"><table class="matrix"><thead><tr>')
    a('    <th class="rowhead">Domain</th>')
    for n, name in LEVELS:
        a(f'    <th>Level {n}<br><small>{name}</small></th>')
    a('  </tr></thead><tbody>')
    for card in u["cards"]:
        a('    <tr>')
        a(f'      <td class="rowhead">{e(card["domain"])}<small>{e(card["mode"])}</small></td>')
        for n, _ in LEVELS:
            lv = card["levels"][n]
            a(f'      <td class="c{n}">')
            a(f'        <span class="cando">{e(lv["canDo"])}</span>')
            a(f'        <span class="sub"><b>Scaffold</b><br>{e(lv["scaffold"])}</span>')
            a(f'        <span class="sub"><b>Check</b><br>{e(lv["check"])}</span>')
            a('      </td>')
        a('    </tr>')
    a('  </tbody></table></div>')

    # worked task
    wt = u["workedTask"]
    a(f'  <h4 style="font-size:13px;font-family:var(--mono);letter-spacing:.1em;'
      f'text-transform:uppercase;color:var(--ink-3);margin-top:8px">'
      f'Worked task &middot; {e(wt["domain"])} &mdash; &ldquo;{e(wt["prompt"])}&rdquo;</h4>')
    a('  <div class="worked">')
    for n, name in LEVELS:
        lv = wt["levels"][n]
        a(f'    <div class="wcard"><div class="wtop t{n}">Level {n} &middot; {name}</div>')
        a(f'      <div class="wbody"><p class="say">&ldquo;{slots(lv["say"])}&rdquo;</p>')
        a(f'      <p class="scaffold"><span class="sl">Scaffold</span>{e(lv["scaffold"])}</p></div></div>')
    a('  </div>')
    a('</article>')
    return "\n".join(out)


def main():
    units = [json.loads(p.read_text()) for p in sorted(UNITS_DIR.glob("u*.json"))]
    if not units:
        print("No units found.", file=sys.stderr)
        return 1

    cards = sum(len(u["cards"]) for u in units)
    out = []
    a = out.append
    a("<title>Brooklyn &mdash; Curriculum Reference</title>")
    css = STYLE.replace("__LIGHT__", LIGHT).replace("__DARK__", DARK)
    a("<style>" + css + "</style>")
    a('<div class="page"><div class="wrap">')

    a('<header class="hero">')
    a('  <div class="eyebrow">Brooklyn &middot; Curriculum Reference</div>')
    a('  <h1>Twelve units, every domain, every level.</h1>')
    a('  <p class="lede">The complete WIDA-aligned newcomer ELD sequence for grades 6&ndash;12. '
      'Every objective below is authored once as an Objective Card and renders to a print packet, '
      'a projector routine, a device task, or small-group cards.</p>')
    a('  <div class="metastrip">')
    a(f'    <span class="chip"><b>{len(units)}</b> units</span>')
    a(f'    <span class="chip"><b>{cards}</b> objective cards</span>')
    a(f'    <span class="chip"><b>{cards * 3}</b> leveled variants</span>')
    a('    <span class="chip"><b>~24</b> weeks</span>')
    a('  </div>')
    a('</header>')

    a('<nav class="toc"><h2>Contents</h2><ol>')
    for u in units:
        a(f'  <li><a href="#u{e(u["no"])}"><span class="n">{e(u["no"])}</span>{e(u["title"])}</a></li>')
    a('</ol></nav>')

    current = None
    for u in units:
        if u["phase"] != current:
            current = u["phase"]
            name, wks = PHASE_NAMES[current]
            a('<div class="phase-head">'
              f'<span class="ph">Phase {current}</span><h2>{name}</h2>'
              f'<span class="wk">{wks}</span></div>')
        a(render_unit(u))

    a('<footer class="legal">Brooklyn &middot; Generated from '
      f'<code>curriculum/units/</code> by <code>tools/build_docs.py</code> &mdash; do not hand-edit.<br>'
      'Independent alignment to the WIDA ELD Standards Framework (2020). Not affiliated with, '
      'authorized by, or endorsed by WIDA / the University of Wisconsin.</footer>')
    a('</div></div>')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out))
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(units)} units, {cards} cards, "
          f"{cards * 3} variants, {OUT.stat().st_size // 1024} KB.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
