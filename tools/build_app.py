#!/usr/bin/env python3
"""Generate the Brooklyn curriculum browser — the teacher-facing app.

Run: python3 tools/build_app.py
Writes: docs/brooklyn-browser.html

Units -> Unit -> Page, with a print tray so a teacher can select any set of pages
across any units and print exactly those. Self-contained single file: the whole
curriculum is inlined, because a file:// page cannot fetch() JSON.

BUILD OUTPUT. Never hand-edit. Edit curriculum/units/*.json and re-run.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
UNITS_DIR = ROOT / "curriculum" / "units"
OUT = ROOT / "docs" / "brooklyn-browser.html"

CSS = r"""
:root{
  --paper:#F4F6F5; --surface:#FFFFFF; --surface-2:#ECF0EE;
  --ink:#17242A; --ink-2:#4B5E64; --ink-3:#616F72;
  --line:#D9E1DE; --line-2:#E7ECEA;
  --accent:#1E6E63; --accent-ink:#124039; --accent-tint:#E1EEEA;
  --warm:#9E541A; --warm-tint:#F3E6D6;
  --lvl1-bg:#E3F1ED; --lvl2-bg:#D2E9E2; --lvl3-bg:#C3E0D7;
  --shadow:0 1px 2px rgba(20,45,40,.05),0 8px 24px -12px rgba(20,45,40,.18);
  --radius:14px;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --serif:Georgia,"Iowan Old Style","Times New Roman",serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,"Cascadia Mono",Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root{
  --paper:#0E181C; --surface:#14232A; --surface-2:#1B2E36;
  --ink:#E8EFEC; --ink-2:#BECCCA; --ink-3:#819697;
  --line:#26383F; --line-2:#203138;
  --accent:#5BC6B4; --accent-ink:#AEE3D8; --accent-tint:#173A38;
  --warm:#E0925A; --warm-tint:#33241A;
  --lvl1-bg:#183531; --lvl2-bg:#1B4B43; --lvl3-bg:#215E53;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px -14px rgba(0,0,0,.6);
}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
     font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
h1,h2,h3,h4{margin:0;line-height:1.15;text-wrap:balance}
p{margin:0}
button{font-family:inherit;cursor:pointer}
a{color:var(--accent);text-decoration:none}

/* ---------- chrome ---------- */
.topbar{position:sticky;top:0;z-index:40;background:var(--surface);
        border-bottom:1px solid var(--line);padding:12px clamp(14px,4vw,32px);
        display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.brand{font-weight:800;letter-spacing:-.02em;font-size:19px;color:var(--ink)}
.brand small{display:block;font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;
             text-transform:uppercase;color:var(--accent);font-weight:600;letter-spacing:.14em}
.crumbs{display:flex;gap:8px;align-items:center;font-size:14px;color:var(--ink-2);flex-wrap:wrap}
.crumbs a{color:var(--ink-2)} .crumbs a:hover{color:var(--accent)}
.crumbs .sep{color:var(--ink-3)}
.spacer{margin-left:auto}
.traybtn{border:1px solid var(--accent);background:var(--accent);color:#fff;font-weight:700;
         font-size:14px;padding:9px 16px;border-radius:10px;display:flex;align-items:center;gap:9px}
@media (prefers-color-scheme:dark){.traybtn{color:#06201c}}
/* transparent + currentColor: contrast follows the button text in both themes.
   A translucent white fill composited to 3.38:1 against white text. */
.traybtn .count{background:transparent;border:1.5px solid currentColor;color:inherit;
                border-radius:999px;padding:0 8px;font-size:12.5px;font-weight:700}
.traybtn[disabled]{opacity:.5;cursor:default}

.wrap{max-width:1120px;margin:0 auto;padding:clamp(20px,4vw,40px) clamp(14px,4vw,32px) 90px}

/* ---------- units grid ---------- */
.lede{color:var(--ink-2);max-width:62ch;margin-bottom:8px}
.phasebar{display:flex;align-items:baseline;gap:12px;margin:34px 0 16px;
          padding-bottom:10px;border-bottom:2px solid var(--accent);flex-wrap:wrap}
.phasebar .ph{font-family:var(--mono);font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;
              background:var(--accent-tint);color:var(--accent-ink);padding:4px 10px;
              border-radius:999px;font-weight:600}
.phasebar h2{font-size:20px}
.phasebar .wk{margin-left:auto;font-family:var(--mono);font-size:12px;color:var(--ink-3)}
.ugrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));gap:16px}
.ucard{display:block;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
       box-shadow:var(--shadow);padding:20px;color:inherit;transition:transform .12s,border-color .12s}
.ucard:hover{transform:translateY(-2px);border-color:var(--accent)}
.ucard .n{font-family:var(--mono);font-size:12.5px;color:var(--accent);font-weight:700;letter-spacing:.1em}
.ucard h3{font-size:19px;margin:6px 0 8px}
.ucard p{font-size:14px;color:var(--ink-2)}
.ucard .doms{display:flex;gap:6px;margin-top:14px;flex-wrap:wrap}
.dchip{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;background:var(--surface-2);
       border:1px solid var(--line);border-radius:6px;padding:3px 7px;color:var(--ink-2)}

/* ---------- unit detail ---------- */
.uhead{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
       box-shadow:var(--shadow);padding:clamp(18px,3vw,28px);margin-bottom:22px}
.uhead .n{font-family:var(--mono);font-size:12.5px;color:var(--accent);font-weight:700;letter-spacing:.1em}
.uhead h1{font-size:clamp(23px,4vw,32px);margin:6px 0 10px}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.chip{font-family:var(--mono);font-size:12px;border:1px solid var(--line);background:var(--surface-2);
      border-radius:999px;padding:5px 11px;color:var(--ink-2)}
.chip b{color:var(--ink)}
.fn{font-family:var(--serif);font-size:16.5px;background:var(--accent-tint);
    border-left:3px solid var(--accent);padding:11px 15px;border-radius:0 8px 8px 0;margin-top:16px}
details.meta{margin-top:16px;border-top:1px solid var(--line-2);padding-top:14px}
details.meta summary{font-family:var(--mono);font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;
                     color:var(--ink-3);font-weight:600;cursor:pointer}
.metagrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px;margin-top:14px}
.box{background:var(--surface-2);border-radius:10px;padding:13px 15px}
.box h4{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;
        color:var(--ink-3);margin-bottom:7px;font-weight:600}
.box ul{margin:0;padding-left:17px;color:var(--ink-2);font-size:14px}
.words{display:flex;flex-wrap:wrap;gap:5px}
.w{font-size:12.5px;background:var(--surface);border:1px solid var(--line);border-radius:6px;
   padding:2px 7px;color:var(--ink-2)}
.note{border:1px solid var(--warm);background:var(--warm-tint);border-radius:10px;padding:13px 15px;margin-top:16px}
.note h4{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;
         color:var(--warm);margin-bottom:5px;font-weight:700}
.note p{font-size:14px}

/* ---------- page picker ---------- */
.pickhead{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin:26px 0 12px}
.pickhead h2{font-size:17px}
.pickhead .hint{font-size:13.5px;color:var(--ink-2)}
.btn{border:1px solid var(--line);background:var(--surface);color:var(--ink);font-size:13px;
     font-weight:600;padding:7px 13px;border-radius:9px}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
@media (prefers-color-scheme:dark){.btn.primary{color:#06201c}}
.matrix{display:grid;grid-template-columns:132px repeat(3,1fr);gap:10px;align-items:stretch}
.mh{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;
    color:var(--ink-3);padding:4px 2px;font-weight:600;align-self:end}
.rowlabel{font-weight:700;font-size:14px;display:flex;flex-direction:column;justify-content:center}
.rowlabel small{font-weight:400;color:var(--ink-3);font-size:11.5px}
.pcell{border:1.5px solid var(--line);border-radius:12px;padding:12px;background:var(--surface);
       display:flex;flex-direction:column;gap:9px;transition:border-color .12s}
.pcell.l1{background:var(--lvl1-bg)}.pcell.l2{background:var(--lvl2-bg)}.pcell.l3{background:var(--lvl3-bg)}
.pcell.sel{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent) inset}
.pcell .cando{font-size:13.5px;color:var(--ink);flex:1}
.pcell .acts{display:flex;gap:8px;align-items:center}
.pcell label{display:flex;align-items:center;gap:7px;font-size:12.5px;color:var(--ink-2);
             font-weight:600;cursor:pointer;user-select:none}
.pcell input[type=checkbox]{width:17px;height:17px;accent-color:var(--accent);cursor:pointer;margin:0}
.pcell a.view{margin-left:auto;font-size:12.5px;font-weight:700;color:var(--accent-ink)}
/* --accent-ink, not --accent: --accent only reached 4.32:1 on the Level 3 cell */
@media (max-width:720px){
  .matrix{grid-template-columns:1fr}
  .mh{display:none}
  .rowlabel{margin-top:14px;border-bottom:1px solid var(--line);padding-bottom:6px}
  .pcell::before{content:attr(data-lvl);font-family:var(--mono);font-size:10.5px;
                 letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);font-weight:700}
}

/* ---------- page view ---------- */
.pageview{display:grid;grid-template-columns:1fr;gap:18px}
.sheetwrap{background:var(--surface-2);border-radius:var(--radius);padding:clamp(12px,3vw,28px)}
.toolrow{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:16px}

/* ---------- the printable sheet ---------- */
.sheet{background:#fff;color:#12181b;width:100%;max-width:8.5in;margin:0 auto 18px;
       padding:.55in .6in;box-shadow:0 6px 26px rgba(0,0,0,.16);font-size:13.5px;line-height:1.55}
.sheet .sh{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;
           border-bottom:2px solid #12181b;padding-bottom:7px}
.sheet .course{font-family:var(--mono);font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:#4a5559}
.sheet h2{font-size:23px;margin-top:3px;color:#12181b}
.sheet .lvlbox{border:1.5px solid #12181b;border-radius:7px;padding:5px 11px;text-align:center;
               font-family:var(--mono);font-size:10.5px;line-height:1.35;white-space:nowrap}
.sheet .idrow{display:flex;gap:26px;margin:14px 0 16px;font-size:13px}
.sheet .idrow span{flex:1;display:flex;gap:8px;align-items:baseline}
.sheet .idrow i{font-style:normal;border-bottom:1px solid #12181b;flex:1}
.sheet .obj{background:#f1f4f3;border-left:3px solid #1E6E63;padding:10px 13px;margin-bottom:16px;font-size:13.5px}
.sheet .obj b{color:#124039}
.sheet .sect{font-family:var(--mono);font-size:11px;letter-spacing:.11em;text-transform:uppercase;
             color:#1E6E63;font-weight:700;margin:16px 0 8px}
.sheet .frame{font-family:var(--serif);font-size:17px;line-height:2.5}
.sheet .blank{display:inline-block;min-width:104px;border-bottom:1.5px solid #12181b;margin:0 5px}
.sheet .lines i{display:block;border-bottom:1px solid #9aa4a7;height:30px}
.sheet .boxes{display:grid;grid-template-columns:repeat(auto-fit,minmax(88px,1fr));gap:9px}
.sheet .abox{border:1.5px solid #12181b;border-radius:8px;height:54px;display:flex;
             align-items:center;justify-content:center;font-family:var(--mono);font-size:12px;color:#4a5559}
.sheet .bank{display:flex;flex-wrap:wrap;gap:7px}
.sheet .bank span{border:1.5px solid #12181b;border-radius:7px;padding:5px 11px;font-family:var(--serif);font-size:14px}
.sheet .imgslot{border:1.5px dashed #9aa4a7;border-radius:8px;padding:16px;text-align:center;
                color:#6b7679;font-size:12px;font-family:var(--mono);margin-bottom:14px}
.sheet .tnote{border:1px solid #c9a98d;background:#fbf5ee;border-radius:8px;padding:11px 13px;margin-top:14px;font-size:12.5px}
.sheet .tnote b{font-family:var(--mono);font-size:10px;letter-spacing:.11em;text-transform:uppercase;color:#8a5a24;display:block;margin-bottom:4px}
.sheet .tgrid{display:grid;gap:10px}
.sheet .trow{border-top:1px solid #dde3e2;padding-top:9px}
.sheet .trow b{font-family:var(--mono);font-size:10px;letter-spacing:.11em;text-transform:uppercase;color:#4a5559;display:block;margin-bottom:3px}
.sheet .foot{border-top:1px solid #dde3e2;margin-top:18px;padding-top:8px;
             font-family:var(--mono);font-size:9.5px;color:#6b7679;display:flex;justify-content:space-between;gap:12px}

/* ---------- tray ---------- */
.scrim{position:fixed;inset:0;background:rgba(8,18,20,.45);z-index:50;opacity:0;pointer-events:none;transition:opacity .18s}
.scrim.open{opacity:1;pointer-events:auto}
.tray{position:fixed;top:0;right:0;height:100%;width:min(420px,100%);background:var(--surface);
      border-left:1px solid var(--line);z-index:60;transform:translateX(100%);transition:transform .22s;
      display:flex;flex-direction:column}
.tray.open{transform:none}
.tray header{padding:18px 20px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:12px}
.tray header h2{font-size:17px}
.tray .x{margin-left:auto;border:0;background:transparent;color:var(--ink-2);font-size:24px;line-height:1;padding:0 4px}
.tray .body{flex:1;overflow:auto;padding:16px 20px}
.tray .foot{border-top:1px solid var(--line);padding:16px 20px;display:flex;flex-direction:column;gap:12px}
.titem{display:flex;gap:11px;align-items:flex-start;padding:11px;border:1px solid var(--line);
       border-radius:10px;margin-bottom:9px;background:var(--surface-2)}
.titem .meta{flex:1;min-width:0}
.titem .t{font-size:13.5px;font-weight:700}
.titem .s{font-size:12px;color:var(--ink-2)}
.titem button{border:0;background:transparent;color:var(--ink-3);font-size:18px;line-height:1;padding:0 2px}
.titem button:hover{color:var(--warm)}
.empty{color:var(--ink-2);font-size:14px;text-align:center;padding:40px 10px}
.segrow{display:flex;gap:0;border:1px solid var(--line);border-radius:10px;overflow:hidden}
.segrow button{flex:1;border:0;background:var(--surface);color:var(--ink-2);font-size:13px;
               font-weight:600;padding:9px 6px}
.segrow button[aria-pressed=true]{background:var(--accent);color:#fff}
@media (prefers-color-scheme:dark){.segrow button[aria-pressed=true]{color:#06201c}}
.copiesrow{display:flex;align-items:center;gap:10px;font-size:13.5px;color:var(--ink-2)}
.copiesrow input{width:64px;padding:7px 9px;border:1px solid var(--line);border-radius:8px;
                 background:var(--surface);color:var(--ink);font-family:inherit;font-size:14px}

/* ---------- print ---------- */
#printArea{display:none}
@media print{
  @page{size:letter portrait;margin:.45in}
  body{background:#fff}
  .topbar,.wrap,.tray,.scrim,.no-print{display:none !important}
  #printArea{display:block}
  .sheet{box-shadow:none;margin:0;padding:0;max-width:none;width:auto;
         break-after:page;page-break-after:always}
  .sheet:last-child{break-after:auto;page-break-after:auto}
  .sheet .imgslot{border-color:#b9c1c0}
}
"""

JS = r"""
var U = window.__BROOKLYN__;
var LEVELS = {1:'Entering',2:'Emerging',3:'Developing'};
var PHASE = {A:['Orientation & Survival','Weeks 1–8'],
             B:['Daily Life & Community','Weeks 9–16'],
             C:['Expanding Language','Weeks 17–24']};
var tray = [], mode = 'student', copies = 1;

try{ var s=localStorage.getItem('brooklyn.tray'); if(s) tray=JSON.parse(s);
     var m=localStorage.getItem('brooklyn.mode'); if(m) mode=m; }catch(e){}
function save(){ try{ localStorage.setItem('brooklyn.tray',JSON.stringify(tray));
                      localStorage.setItem('brooklyn.mode',mode); }catch(e){} }

function esc(s){return String(s).replace(/[&<>"]/g,function(c){
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function unit(no){return U.filter(function(u){return u.no===no;})[0];}
function card(u,d){return u.cards.filter(function(c){return c.domain===d;})[0];}
function key(t){return t.u+'|'+t.d+'|'+t.l;}
function inTray(t){return tray.some(function(x){return key(x)===key(t);});}
function studentCanDo(s){return 'I can '+s.charAt(0).toLowerCase()+s.slice(1);}

/* ---------------- sheets ---------------- */
function taskArea(u,c,lv,l){
  var wt=u.workedTask, out='';
  if(wt.domain===c.domain && wt.levels[l]){
    var frame=esc(wt.levels[l].say).replace(/\[([^\]]+)\]/g,'<span class="blank"></span>');
    out+='<div class="sect">Say it</div><div class="frame">“'+frame+'”</div>';
  }
  if(c.domain==='Listening'||c.domain==='Reading'){
    out+='<div class="sect">Your answers</div><div class="boxes">'+
         [1,2,3,4].map(function(n){return '<div class="abox">'+n+'</div>';}).join('')+'</div>';
  }
  if(c.domain==='Writing'){
    var n = l==='1'?4:(l==='2'?5:7);
    out+='<div class="sect">Write here</div><div class="lines">'+
         Array(n).fill('<i></i>').join('')+'</div>';
  }
  if(c.domain==='Speaking' && wt.domain!==c.domain){
    out+='<div class="sect">Practice with a partner</div><div class="boxes">'+
         ['1st try','2nd try','3rd try'].map(function(t){return '<div class="abox">'+t+'</div>';}).join('')+'</div>';
  }
  return out;
}

function studentSheet(u,c,l){
  var lv=c.levels[l], bank=u.vocabulary.core.slice(0,10);
  return '<section class="sheet">'+
   '<div class="sh"><div><div class="course">Brooklyn · Unit '+esc(u.no)+' · '+esc(u.title)+'</div>'+
   '<h2>'+esc(u.function)+'</h2></div>'+
   '<div class="lvlbox">Level '+l+'<br>'+LEVELS[l]+'<br>'+esc(c.domain)+'</div></div>'+
   '<div class="idrow"><span>Name: <i></i></span><span>Date: <i></i></span></div>'+
   '<div class="obj"><b>'+esc(studentCanDo(lv.canDo))+'</b></div>'+
   '<div class="imgslot">Picture support goes here — not yet produced</div>'+
   taskArea(u,c,l,l)+
   '<div class="sect">Word bank</div><div class="bank">'+
     bank.map(function(w){return '<span>'+esc(w)+'</span>';}).join('')+'</div>'+
   '<div class="foot"><span>Brooklyn · '+esc(c.id)+' · L'+l+'</span>'+
   '<span>WIDA (2020), independent alignment</span></div></section>';
}

function teacherSheet(u,c,l){
  var lv=c.levels[l];
  return '<section class="sheet">'+
   '<div class="sh"><div><div class="course">Brooklyn · Teacher page · Unit '+esc(u.no)+'</div>'+
   '<h2>'+esc(u.title)+'</h2></div>'+
   '<div class="lvlbox">Level '+l+'<br>'+LEVELS[l]+'<br>'+esc(c.domain)+'</div></div>'+
   '<div class="obj"><b>Can-Do:</b> '+esc(lv.canDo)+'<br><b>WIDA:</b> '+
     esc(u.standards.wida.standards.join(' · '))+' · '+esc(c.domain)+
     ' · <b>Key Use:</b> '+esc(u.standards.wida.keyUses.join(', '))+'</div>'+
   '<div class="tgrid">'+
     '<div class="trow"><b>Scaffold</b>'+esc(lv.scaffold)+'</div>'+
     '<div class="trow"><b>Home-language bridge</b>'+esc(lv.l1Bridge)+'</div>'+
     '<div class="trow"><b>Check</b>'+esc(lv.check)+'</div>'+
     '<div class="trow"><b>Target structures</b>'+esc(u.grammar.join(' · '))+'</div>'+
     '<div class="trow"><b>Foundational literacy</b>'+esc(u.foundationalLiteracy)+'</div>'+
   '</div>'+
   (u.culturalNote?'<div class="tnote"><b>Teaching note — read before you teach this</b>'+esc(u.culturalNote)+'</div>':'')+
   '<div class="foot"><span>Brooklyn · '+esc(c.id)+' · L'+l+' · teacher</span>'+
   '<span>Formative evidence — not a proficiency-level measure</span></div></section>';
}

function sheetsFor(t){
  var u=unit(t.u), c=card(u,t.d), out=[];
  if(mode==='student'||mode==='both') out.push(studentSheet(u,c,t.l));
  if(mode==='teacher'||mode==='both') out.push(teacherSheet(u,c,t.l));
  return out.join('');
}

/* ---------------- views ---------------- */
function viewUnits(){
  var h='<p class="lede">Twelve units. Open a unit, pick the pages you need, and print exactly those — '+
        'each level is a separate page, so a mixed-level class is one trip to the printer.</p>';
  ['A','B','C'].forEach(function(p){
    var us=U.filter(function(u){return u.phase===p;});
    if(!us.length) return;
    h+='<div class="phasebar"><span class="ph">Phase '+p+'</span><h2>'+PHASE[p][0]+
       '</h2><span class="wk">'+PHASE[p][1]+'</span></div><div class="ugrid">';
    us.forEach(function(u){
      h+='<a class="ucard" href="#/u'+u.no+'"><div class="n">Unit '+esc(u.no)+' · '+esc(u.weeks)+'</div>'+
         '<h3>'+esc(u.title)+'</h3><p>'+esc(u.focus)+'</p><div class="doms">'+
         u.cards.map(function(c){return '<span class="dchip">'+esc(c.domain)+'</span>';}).join('')+
         '<span class="dchip">3 levels</span></div></a>';
    });
    h+='</div>';
  });
  return h;
}

function viewUnit(no){
  var u=unit(no); if(!u) return '<p>Unit not found.</p>';
  var h='<div class="uhead"><div class="n">Unit '+esc(u.no)+' · '+esc(u.weeks)+' · Phase '+u.phase+'</div>'+
    '<h1>'+esc(u.title)+'</h1><p class="lede">'+esc(u.focus)+'</p>'+
    '<div class="chips"><span class="chip"><b>WIDA</b> '+esc(u.standards.wida.standards.join(' · '))+'</span>'+
    '<span class="chip"><b>Key Use</b> '+esc(u.standards.wida.keyUses.join(', '))+'</span></div>'+
    '<p class="fn">'+esc(u.function)+'</p>'+
    '<details class="meta"><summary>Unit detail — structures, vocabulary, teaching note</summary><div class="metagrid">'+
      '<div class="box"><h4>Target structures</h4><ul>'+u.grammar.map(function(g){return '<li>'+esc(g)+'</li>';}).join('')+'</ul></div>'+
      '<div class="box"><h4>Foundational literacy</h4><p style="font-size:14px;color:var(--ink-2)">'+esc(u.foundationalLiteracy)+'</p></div>'+
      '<div class="box"><h4>Core vocabulary</h4><div class="words">'+u.vocabulary.core.map(function(w){return '<span class="w">'+esc(w)+'</span>';}).join('')+'</div></div>'+
      '<div class="box"><h4>Academic vocabulary</h4><div class="words">'+u.vocabulary.academic.map(function(w){return '<span class="w">'+esc(w)+'</span>';}).join('')+'</div></div>'+
    '</div>'+(u.culturalNote?'<div class="note"><h4>Teaching note</h4><p>'+esc(u.culturalNote)+'</p></div>':'')+'</details></div>';

  h+='<div class="pickhead"><h2>Pages</h2><span class="hint">Tick any pages, then print them together.</span>'+
     '<span class="spacer"></span>'+
     '<button class="btn" data-all="'+u.no+'">Select all 12</button>'+
     '<button class="btn" data-none="'+u.no+'">Clear</button></div>';

  h+='<div class="matrix"><div class="mh">Domain</div>'+
     [1,2,3].map(function(l){return '<div class="mh">Level '+l+' · '+LEVELS[l]+'</div>';}).join('');
  u.cards.forEach(function(c){
    h+='<div class="rowlabel">'+esc(c.domain)+'<small>'+esc(c.mode)+'</small></div>';
    [1,2,3].forEach(function(l){
      var t={u:u.no,d:c.domain,l:String(l)}, on=inTray(t);
      h+='<div class="pcell l'+l+(on?' sel':'')+'" data-lvl="Level '+l+' · '+LEVELS[l]+'">'+
         '<div class="cando">'+esc(c.levels[l].canDo)+'</div><div class="acts">'+
         '<label><input type="checkbox" data-t="'+u.no+'|'+c.domain+'|'+l+'"'+(on?' checked':'')+'> Print</label>'+
         '<a class="view" href="#/u'+u.no+'/'+c.domain.toLowerCase()+'/'+l+'">Open →</a></div></div>';
    });
  });
  return h+'</div>';
}

function viewPage(no,dom,l){
  var u=unit(no); if(!u) return '<p>Not found.</p>';
  var c=u.cards.filter(function(x){return x.domain.toLowerCase()===dom;})[0];
  if(!c||!c.levels[l]) return '<p>Page not found.</p>';
  var t={u:no,d:c.domain,l:l}, on=inTray(t);
  return '<div class="toolrow">'+
    '<button class="btn primary" id="addOne">'+(on?'✓ In print tray':'+ Add to print tray')+'</button>'+
    '<button class="btn" id="printOne">Print this page</button>'+
    '<span class="spacer"></span>'+
    '<div class="segrow" style="max-width:290px">'+
      ['student','teacher','both'].map(function(m){
        return '<button data-mode="'+m+'" aria-pressed="'+(mode===m)+'">'+m[0].toUpperCase()+m.slice(1)+'</button>';}).join('')+
    '</div></div>'+
    '<div class="sheetwrap">'+sheetsFor(t)+'</div>';
}

/* ---------------- tray ---------------- */
function renderTray(){
  var b=document.getElementById('trayBody');
  if(!tray.length){ b.innerHTML='<div class="empty">No pages selected yet.<br>Open a unit and tick the pages you want.</div>'; }
  else{
    b.innerHTML=tray.map(function(t,i){
      var u=unit(t.u), c=card(u,t.d);
      return '<div class="titem"><div class="meta"><div class="t">Unit '+esc(t.u)+' · '+esc(t.d)+' · L'+t.l+'</div>'+
        '<div class="s">'+esc(u.title)+' — '+esc(c.levels[t.l].canDo)+'</div></div>'+
        '<button data-rm="'+i+'" title="Remove">×</button></div>';
    }).join('');
  }
  document.getElementById('trayCount').textContent=tray.length;
  document.getElementById('trayBtn').disabled = !tray.length;
  document.getElementById('printBtn').disabled = !tray.length;
  document.querySelectorAll('#trayModes button').forEach(function(x){
    x.setAttribute('aria-pressed', String(x.dataset.mode===mode));});
  buildPrint();
}

function buildPrint(){
  var n=Math.max(1,Math.min(40,copies|0)), out='';
  for(var r=0;r<n;r++) tray.forEach(function(t){ out+=sheetsFor(t); });
  document.getElementById('printArea').innerHTML=out;
}

function toggle(t,on){
  var i=tray.findIndex(function(x){return key(x)===key(t);});
  if(on&&i<0) tray.push(t);
  if(!on&&i>=0) tray.splice(i,1);
  save(); renderTray();
}

/* ---------------- routing ---------------- */
function crumbs(p){
  var h='<a href="#/">All units</a>';
  if(p[0]){var u=unit(p[0]); if(u) h+='<span class="sep">/</span><a href="#/u'+u.no+'">Unit '+u.no+' · '+esc(u.title)+'</a>';}
  if(p[1]) h+='<span class="sep">/</span><span>'+esc(p[1][0].toUpperCase()+p[1].slice(1))+' · Level '+p[2]+'</span>';
  return h;
}

function route(){
  var m=(location.hash||'#/').replace(/^#\/?/,'').split('/').filter(Boolean);
  var main=document.getElementById('main'), p=[];
  if(!m.length){ main.innerHTML=viewUnits(); }
  else if(m[0][0]==='u'&&m.length===1){ p=[m[0].slice(1)]; main.innerHTML=viewUnit(p[0]); }
  else if(m[0][0]==='u'&&m.length===3){ p=[m[0].slice(1),m[1],m[2]]; main.innerHTML=viewPage(p[0],m[1],m[2]); }
  else main.innerHTML='<p>Not found. <a href="#/">Back to units</a></p>';
  document.getElementById('crumbs').innerHTML=crumbs(p);
  window.scrollTo(0,0);
  renderTray();
}

document.addEventListener('click',function(ev){
  var el=ev.target;
  if(el.id==='trayBtn'||el.id==='trayClose'||el.classList.contains('scrim')){
    document.getElementById('tray').classList.toggle('open', el.id==='trayBtn');
    document.getElementById('scrim').classList.toggle('open', el.id==='trayBtn');
  }
  if(el.dataset.rm!==undefined){ tray.splice(+el.dataset.rm,1); save(); renderTray(); route(); }
  if(el.dataset.all){ var u=unit(el.dataset.all);
    u.cards.forEach(function(c){[1,2,3].forEach(function(l){
      var t={u:u.no,d:c.domain,l:String(l)}; if(!inTray(t)) tray.push(t);});});
    save(); route(); }
  if(el.dataset.none){ tray=tray.filter(function(t){return t.u!==el.dataset.none;}); save(); route(); }
  if(el.dataset.mode){ mode=el.dataset.mode; save(); route(); }
  if(el.id==='clearAll'){ tray=[]; save(); route(); }
  if(el.id==='printBtn'){ buildPrint(); window.print(); }
  if(el.id==='addOne'){
    var m=location.hash.replace(/^#\/?/,'').split('/');
    var u=unit(m[0].slice(1)), c=u.cards.filter(function(x){return x.domain.toLowerCase()===m[1];})[0];
    var t={u:u.no,d:c.domain,l:m[2]}; toggle(t,!inTray(t)); route(); }
  if(el.id==='printOne'){
    var m2=location.hash.replace(/^#\/?/,'').split('/');
    var u2=unit(m2[0].slice(1)), c2=u2.cards.filter(function(x){return x.domain.toLowerCase()===m2[1];})[0];
    document.getElementById('printArea').innerHTML=sheetsFor({u:u2.no,d:c2.domain,l:m2[2]});
    window.print(); setTimeout(buildPrint,600); }
});

document.addEventListener('change',function(ev){
  var el=ev.target;
  if(el.dataset.t){ var a=el.dataset.t.split('|'); toggle({u:a[0],d:a[1],l:a[2]}, el.checked);
    el.closest('.pcell').classList.toggle('sel', el.checked); }
  if(el.id==='copies'){ copies=Math.max(1,Math.min(40,+el.value||1)); buildPrint(); }
});

window.addEventListener('hashchange',route);
route();
"""


def main():
    units = [json.loads(p.read_text()) for p in sorted(UNITS_DIR.glob("u*.json"))]
    if not units:
        print("No units found.", file=sys.stderr)
        return 1

    data = json.dumps(units, ensure_ascii=False, separators=(",", ":"))
    pages = sum(len(u["cards"]) for u in units) * 3

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Brooklyn &mdash; Curriculum Browser</title>
<style>{CSS}</style>
</head>
<body>
<div class="topbar no-print">
  <div class="brand"><small>Brooklyn</small>Curriculum</div>
  <nav class="crumbs" id="crumbs"></nav>
  <span class="spacer"></span>
  <button class="traybtn" id="trayBtn">Print tray <span class="count" id="trayCount">0</span></button>
</div>

<main class="wrap" id="main"></main>

<div class="scrim no-print" id="scrim"></div>
<aside class="tray no-print" id="tray" aria-label="Print tray">
  <header><h2>Print tray</h2><button class="x" id="trayClose" aria-label="Close">&times;</button></header>
  <div class="body" id="trayBody"></div>
  <div class="foot">
    <div class="segrow" id="trayModes">
      <button data-mode="student">Student</button>
      <button data-mode="teacher">Teacher</button>
      <button data-mode="both">Both</button>
    </div>
    <div class="copiesrow">
      <label for="copies">Copies of each set</label>
      <input id="copies" type="number" min="1" max="40" value="1">
    </div>
    <button class="btn primary" id="printBtn">Print selected pages</button>
    <button class="btn" id="clearAll">Clear tray</button>
  </div>
</aside>

<div id="printArea"></div>

<script>window.__BROOKLYN__ = {data};</script>
<script>{JS}</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(units)} units, {pages} printable pages, "
          f"{OUT.stat().st_size // 1024} KB.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
