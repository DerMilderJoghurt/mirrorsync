TEMPLATES = {
"base.html": r"""<!doctype html>
<html lang="{{ lang_code() }}"{% if side_mini %} data-side="mini"{% endif %}><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% block title %}MirrorSync{% endblock %} · MirrorSync</title><link rel="icon" href="/static/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/static/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#4f46e5" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#09090b" media="(prefers-color-scheme: dark)"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes">
{% if auto_refresh %}<script>/* Seite alle 3 s neu laden, aber nicht, solange das Aufträge-Fenster, ein Menü oder ein Dialog offen ist oder Text markiert wird */
setInterval(()=>{const tp=document.getElementById('taskpop');if((tp&&!tp.hidden)||document.querySelector('details[open].pausemenu,dialog[open],.fmmenu[open]')||String(window.getSelection&&getSelection())!==''||document.hidden)return;location.reload()},3000);</script>{% endif %}
<script>try{const t=localStorage.getItem('ms-theme');if(t)document.documentElement.dataset.theme=t}catch(e){}</script>
<style>
:root{--bg:#f6f7f9;--side:#ffffff;--card:#ffffff;--card2:#f9fafb;--fg:#0f172a;--mut:#64748b;--bd:#e5e7eb;--bd2:#d1d5db;
--acc:#4f46e5;--acc-fg:#fff;--acc-soft:rgba(79,70,229,.10);--ok:#16a34a;--ok-soft:rgba(22,163,74,.12);--err:#dc2626;--err-soft:rgba(220,38,38,.10);
--warn:#d97706;--warn-soft:rgba(217,119,6,.12);--run:#2563eb;--run-soft:rgba(37,99,235,.12);--shadow:0 1px 2px rgba(15,23,42,.05)}
:root[data-theme=dark]{--bg:#09090b;--side:#0c0c0f;--card:#111114;--card2:#16161a;--fg:#ececf1;--mut:#8b8b98;--bd:#232329;--bd2:#2e2e36;
--acc:#8b93ff;--acc-fg:#0b0b10;--acc-soft:rgba(139,147,255,.14);--ok:#4ade80;--ok-soft:rgba(74,222,128,.12);--err:#f87171;--err-soft:rgba(248,113,113,.12);
--warn:#fbbf24;--warn-soft:rgba(251,191,36,.12);--run:#60a5fa;--run-soft:rgba(96,165,250,.14);--shadow:none}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#09090b;--side:#0c0c0f;--card:#111114;--card2:#16161a;--fg:#ececf1;--mut:#8b8b98;--bd:#232329;--bd2:#2e2e36;
--acc:#8b93ff;--acc-fg:#0b0b10;--acc-soft:rgba(139,147,255,.14);--ok:#4ade80;--ok-soft:rgba(74,222,128,.12);--err:#f87171;--err-soft:rgba(248,113,113,.12);
--warn:#fbbf24;--warn-soft:rgba(251,191,36,.12);--run:#60a5fa;--run-soft:rgba(96,165,250,.14);--shadow:none}}
*{box-sizing:border-box}html,body{height:100%}
body{margin:0;font:14px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Inter,sans-serif;background:var(--bg);color:var(--fg);-webkit-font-smoothing:antialiased}
a{color:var(--acc)}code{font:12.5px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--card2);border:1px solid var(--bd);padding:1px 5px;border-radius:5px}
.app{display:flex;min-height:100vh}
aside{width:232px;flex:0 0 232px;background:var(--side);border-right:1px solid var(--bd);display:flex;flex-direction:column;position:sticky;top:0;height:100vh}
.brand{display:flex;align-items:center;gap:10px;padding:18px 18px 22px;font-weight:650;font-size:15px;letter-spacing:-.01em}
.logo{width:30px;height:30px;border-radius:8px;background:linear-gradient(135deg,var(--acc),#a855f7);display:grid;place-items:center;color:#fff}
nav{display:flex;flex-direction:column;gap:2px;padding:0 10px}
nav a{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;color:var(--mut);text-decoration:none;font-weight:500}
nav a:hover{background:var(--card2);color:var(--fg)}nav a.active{background:var(--acc-soft);color:var(--acc)}
nav svg,.btn svg{width:16px;height:16px;flex:0 0 16px}
.side-foot{margin-top:auto;padding:12px 10px;border-top:1px solid var(--bd);display:flex;flex-direction:column;gap:2px}
.side-foot .ver{color:var(--mut);font-size:12px;padding:6px 10px}.side-foot .ver .upd{color:var(--acc);font-weight:600;text-decoration:none}.side-foot .ver .upd:hover{text-decoration:underline}.side-foot .ver .vlink{color:inherit;text-decoration:none}.side-foot .ver .vlink:hover{color:var(--fg);text-decoration:underline}
.side-foot button,.side-foot a{all:unset;display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;color:var(--mut);cursor:pointer;font-weight:500}
.side-foot button:hover,.side-foot a:hover{background:var(--card2);color:var(--fg)}.side-foot svg{width:16px;height:16px}
.content{flex:1;min-width:0}
aside{transition:width .18s ease,flex-basis .18s ease}.brand{position:static}.lbl{white-space:nowrap;overflow:hidden}
.sidetog{all:unset;position:absolute;right:-13px;top:50%;margin-top:-13px;width:24px;height:24px;display:grid;place-items:center;border-radius:50%;background:var(--card);border:1px solid var(--bd2);box-shadow:0 1px 4px rgba(0,0,0,.12);color:var(--mut);cursor:pointer;z-index:20}
.sidetog:hover{background:var(--card2);color:var(--fg)}.sidetog svg{width:14px;height:14px;transition:transform .18s}
.btn,form.inline,details.pausemenu{vertical-align:middle}
html:has(dialog[open]),html:has(dialog[open]) body{overflow:hidden}dialog[open]{overscroll-behavior:contain;max-height:88vh;overflow:auto}dialog::backdrop{background:rgba(0,0,0,.45)}
:root[data-side=mini] aside{width:64px;flex-basis:64px}:root[data-side=mini] aside .lbl,:root[data-side=mini] .side-foot .ver{display:none}
:root[data-side=mini] .brand{flex-direction:column;padding:18px 0 14px;gap:8px}:root[data-side=mini] .sidetog svg{transform:rotate(180deg)}
:root[data-side=mini] nav{padding:0 10px}:root[data-side=mini] nav a,:root[data-side=mini] .side-foot button,:root[data-side=mini] .side-foot a{justify-content:center;padding:9px 0;position:relative}
:root[data-side=mini] nav a .badge{position:absolute;top:2px;right:2px;margin:0;font-size:10px;padding:0 4px}:root[data-side=mini] .userchip{padding:6px 0}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:22px 32px 6px;flex-wrap:wrap}
.topbar h1{margin:0;font-size:22px;font-weight:650;letter-spacing:-.02em}.topbar p{margin:2px 0 0;color:var(--mut)}
main{padding:16px 32px 40px;max-width:none;width:100%;box-sizing:border-box}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:20px;margin-bottom:16px;box-shadow:var(--shadow)}
.card h2,.card h3{margin:0 0 4px;font-size:15px;font-weight:600}.card h2{font-size:16px}
.card-head{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:16px}
.stat{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px 18px;box-shadow:var(--shadow)}
.stat .k{color:var(--mut);font-size:12.5px;font-weight:500}.stat .v{font-size:24px;font-weight:650;letter-spacing:-.02em;margin-top:2px}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:11px 10px;border-bottom:1px solid var(--bd);vertical-align:middle}
tr:last-child td{border-bottom:0}th{color:var(--mut);font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
td small,.mut{color:var(--mut)}
.nextrun{margin-top:3px}.nextrun b{color:var(--fg);font-weight:600;white-space:nowrap}
.btn{display:inline-flex;align-items:center;gap:6px;height:34px;padding:0 13px;border:1px solid var(--bd2);border-radius:8px;background:var(--card);color:var(--fg);cursor:pointer;text-decoration:none;font:inherit;font-weight:500;font-size:13.5px;white-space:nowrap;transition:background .12s,border-color .12s}
.btn:hover{background:var(--card2)}.btn.pri{background:var(--acc);border-color:var(--acc);color:var(--acc-fg)}.btn.pri:hover{filter:brightness(1.08)}
.btn.del{color:var(--err)}.btn.del:hover{background:var(--err-soft);border-color:var(--err)}.btn.sm{height:30px;padding:0 10px;font-size:13px}
.btn.icon{width:34px;padding:0;justify-content:center}
form.inline{display:inline}
.tag{white-space:nowrap;display:inline-flex;align-items:center;gap:5px;padding:2px 9px;border-radius:99px;font-size:12px;font-weight:550;background:var(--card2);color:var(--mut)}
.tag::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}
.tag.ok{background:var(--ok-soft);color:var(--ok)}.tag.fehler,.tag.abgebrochen{background:var(--err-soft);color:var(--err)}
.tag.laeuft{background:var(--run-soft);color:var(--run)}.tag.gestoppt,.tag.freigabe{background:var(--warn-soft);color:var(--warn)}
.ok{color:var(--ok)}.fehler,.abgebrochen{color:var(--err)}.laeuft{color:var(--run)}.gestoppt{color:var(--warn)}
label{display:block;margin:14px 0 5px;font-weight:550;font-size:13.5px}
input[type=text],input[type=number],input[type=date],input[type=password],input[type=email],input[type=time],input[type=datetime-local],select,textarea{width:100%;height:36px;padding:0 11px;border:1px solid var(--bd2);border-radius:8px;background:var(--card2);color:var(--fg);font:inherit;outline:none;transition:border-color .12s,box-shadow .12s}
textarea{height:auto;padding:9px 11px;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
input:focus,select:focus,textarea:focus{border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}
.row{display:flex;gap:12px}.row>*{flex:1;min-width:0}.hint{color:var(--mut);font-size:12.5px;margin-top:5px}
.check{display:flex;gap:9px;align-items:flex-start;font-weight:400;margin:8px 0}.check input{margin-top:3px;accent-color:var(--acc)}
pre{background:var(--card2);border:1px solid var(--bd);border-radius:10px;padding:14px;overflow:auto;max-height:65vh;white-space:pre-wrap;font:12.5px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
pre.lines span{display:block}pre.lines .error{color:var(--err);background:var(--err-soft)}pre.lines .copied{color:var(--ok)}pre.lines .deleted{color:var(--warn)}pre.lines .notice{color:var(--mut)}
tr.click{cursor:pointer}tr.click:hover td{background:var(--card2)}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0 12px}.chip{display:inline-flex;gap:6px;align-items:center;padding:5px 11px;border:1px solid var(--bd2);border-radius:999px;color:var(--mut);text-decoration:none;font-size:13px}
.chip b{color:var(--fg);font-weight:600}.chip.active{border-color:var(--acc);background:var(--acc-soft);color:var(--acc)}.chip.active b{color:var(--acc)}
.bwrow{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap;padding:12px;border:1px solid var(--bd);border-radius:10px;margin-bottom:8px;background:var(--card2)}
.bwrow label{margin:0 0 4px;font-size:12.5px}.bwrow input[type=time],.bwrow input.mb{width:120px;background:var(--card)}:root[data-theme=dark] input[type=time],:root[data-theme=dark] input[type=datetime-local]{color-scheme:dark}@media (prefers-color-scheme:dark){:root:not([data-theme=light]) input[type=time],:root:not([data-theme=light]) input[type=datetime-local]{color-scheme:dark}}
.days{display:flex;gap:4px}.days label{margin:0;display:inline-flex}.days input{display:none}.days span{display:inline-block;padding:6px 9px;border:1px solid var(--bd2);border-radius:7px;cursor:pointer;font-size:13px;user-select:none}
.days input:checked+span{background:var(--acc);border-color:var(--acc);color:var(--acc-fg)}
.bwprev{font-size:13px;color:var(--mut);margin-top:6px}
.seg{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px}.seg label{margin:0;display:inline-flex}.seg input{display:none}
.seg span{padding:8px 13px;border:1px solid var(--bd2);border-radius:8px;cursor:pointer;font-weight:500;background:var(--card2)}.seg input:checked+span{border-color:var(--acc);background:var(--acc-soft);color:var(--acc)}
.chain{color:var(--mut);margin-right:4px}
.sch{display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap;padding:12px;border:1px solid var(--bd);border-radius:10px;margin-bottom:8px;background:var(--card2)}
.sch .nm{flex:1 1 160px;min-width:0}.chainhead .nm b{display:block}.sch .nm b{display:block}.sch .nm .path{font-size:12px}.sch .ctl{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.sch select,.sch input[type=time],.sch input[type=text],.sch input[type=number]{width:auto;height:32px}.sch .days span{padding:4px 7px}
.chainbox{border:1px solid var(--bd);border-radius:12px;padding:12px;margin-bottom:14px}
.chainhead{display:flex;gap:10px;align-items:center;padding:10px 12px;border-radius:10px;background:var(--acc-soft);margin-bottom:6px}
.drop{min-height:44px;border-radius:10px;padding:2px 0}.drop.over{outline:2px dashed var(--acc);outline-offset:2px}
.drop .sch{cursor:grab;margin-left:22px;position:relative}.drop .sch:before{content:"↓";position:absolute;left:-18px;top:14px;color:var(--mut)}
.drop .sch.dragging{opacity:.4}.handle{cursor:grab;color:var(--mut);font-size:18px;line-height:32px;user-select:none}
.empty-drop{color:var(--mut);font-size:13px;padding:12px;border:1px dashed var(--bd2);border-radius:10px;margin-left:22px}
.savestate{font-size:13px;color:var(--mut)}
table.chg{width:auto;margin-top:2px}table.chg td{border:0;padding:1px 10px 1px 0;font-size:12.5px;vertical-align:top;word-break:break-word}
table.chg del{color:var(--err);text-decoration:line-through;opacity:.8}table.chg ins{color:var(--ok);text-decoration:none}
table.audit>tbody>tr>td{vertical-align:top}
@media(max-width:760px){form.afilter{align-items:stretch!important}form.afilter>div{flex:1 1 100%!important}
table.audit th:nth-child(3),table.audit td:nth-child(3){display:none}table.audit td{font-size:13px}}
details.tpl{border:1px solid var(--bd);border-radius:10px;margin:8px 0;background:var(--card2)}
details.tpl>summary{cursor:pointer;padding:10px 12px;list-style:none;display:flex;gap:8px;align-items:center}
details.tpl>summary::-webkit-details-marker{display:none}details.tpl>summary:before{content:"▸";color:var(--mut)}details.tpl[open]>summary:before{content:"▾"}
.tplbody{padding:0 12px 12px}.tplbody textarea{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}
button.chip{background:transparent;font:inherit;font-size:13px}.vars .chip{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;cursor:pointer}
.preview{border:1px dashed var(--bd2);border-radius:8px;padding:10px 12px;background:var(--card);margin:0}
.preview .pt{font-weight:600;margin-bottom:6px}.preview pre.pb,pre.preview{border:0;background:none;padding:0;box-shadow:none}pre.preview{border:1px dashed var(--bd2);padding:10px 12px;background:var(--card)}.preview pre,pre.preview{white-space:pre-wrap;word-break:break-word;margin:0;font:13px/1.5 inherit;font-family:inherit}
tr.paused>td{opacity:.62}tr.paused>td:last-child{opacity:1}.tag.pausetag{background:var(--warn-soft,rgba(217,119,6,.12));color:var(--warn,#d97706)}
details.pausemenu{display:inline-block;position:relative}details.pausemenu>summary{list-style:none;display:inline-flex}details.pausemenu>summary::-webkit-details-marker{display:none}
.pmenu{position:absolute;right:0;top:calc(100% + 4px);z-index:20;background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:10px;box-shadow:0 8px 24px rgba(0,0,0,.15);display:flex;flex-direction:column;gap:6px;min-width:220px;text-align:left;white-space:normal}
.pmenu form{margin:0}.pmenu form>.btn{width:100%;justify-content:flex-start}.pmenu .pdate{display:flex;gap:6px}.pmenu .pdate input{height:32px;flex:1}
.fbpanel{position:fixed;top:0;right:0;bottom:0;width:clamp(340px,42vw,860px);background:var(--card);border-left:1px solid var(--bd);z-index:60;
 display:flex;flex-direction:column;padding:14px 16px;gap:8px;transform:translateX(105%);transition:transform .18s ease;box-shadow:-12px 0 32px rgba(0,0,0,.18)}
body.fb-open .fbpanel{transform:none}.fbshade{display:none}
@media(min-width:1400px){body.fb-open main{padding-right:calc(clamp(340px,42vw,860px) + 24px)}}
@media(max-width:1399px){body.fb-open .fbshade{display:block;position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:59}}
@media(max-width:700px){.fbpanel{width:100vw;padding:12px}}
.fbtop{display:flex;gap:6px;align-items:center}.fbtop input{width:min(240px,40vw);height:32px}
.fbcrumbs{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;word-break:break-all}.fbcrumbs a{text-decoration:none}.fbcrumbs .sep{color:var(--mut);margin:0 6px}
.fbtable{flex:1;overflow:auto;border:1px solid var(--bd);border-radius:8px}
#fbt{width:100%}#fbt th{position:sticky;top:0;background:var(--card);z-index:1;cursor:pointer;user-select:none}
#fbt th[data-dir]:not([data-dir=""])::after{content:" " attr(data-dir);font-size:10px}#fbt td{padding:6px 10px}#fbt .num{text-align:right;white-space:nowrap}
#fbt tr.fdir a{text-decoration:none;color:var(--fg);font-weight:500}#fbt tr.ffile span{color:var(--fg)}#fbt .mob{display:none;font-size:12px}
#fbt tr.picked td{background:var(--acc-soft,rgba(59,130,246,.10))}#fbt .fbck{width:16px;height:16px;margin:0 6px 0 0;vertical-align:-3px;accent-color:var(--acc,#2563eb)}
#fbt tr.excluded td{opacity:.55;text-decoration:line-through}#fbt .exb{padding:1px 6px;text-decoration:none}#fbt .exb.on{background:var(--err-soft);border-color:var(--err)}
@media(max-width:700px){ #fbt .mob{display:block}}
.fbfoot{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.fbuse code{font-size:12px;background:none;color:inherit}
#manual-drop .sch{margin-left:0}#manual-drop .sch:before{content:none}
.badge{display:inline-grid;place-items:center;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--err);color:#fff;font-size:11px;font-weight:700;margin-left:auto}
.tabs .badge{margin-left:6px}tr.new td{background:var(--err-soft)}
.num{font-variant-numeric:tabular-nums}.num.err{color:var(--err);font-weight:600}
.msg{padding:11px 14px;border-radius:10px;margin-bottom:14px;white-space:pre-wrap;border:1px solid}
.msg.ok{border-color:var(--ok);background:var(--ok-soft);color:var(--fg)}.msg.err{border-color:var(--err);background:var(--err-soft);color:var(--fg)}
.msg.info{border-color:var(--bd2);background:var(--acc-soft);color:var(--fg)}
.browse{border:1px solid var(--bd);border-radius:8px;margin-top:6px;max-height:230px;overflow:auto;display:none;background:var(--card2)}
.browse div{padding:6px 11px;cursor:pointer}.browse div:hover{background:var(--acc-soft)}
details summary{cursor:pointer;color:var(--mut);font-weight:500}
.section{border-top:1px solid var(--bd);margin-top:20px;padding-top:6px}
.section>h3{margin:12px 0 0}
.jobname{font-weight:600}.path{font:12.5px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--mut);word-break:break-all}
.empty{text-align:center;padding:36px 10px;color:var(--mut)}
.mobile-nav{display:none}
.userchip{gap:10px!important;align-items:center!important}.userchip b{color:var(--fg);font-weight:600}.userchip small{font-size:11.5px}
.avatar{width:28px;height:28px;border-radius:50%;background:var(--acc-soft);color:var(--acc);display:grid;place-items:center;font-weight:700;font-size:13px;flex:0 0 28px}
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--bd);margin:-4px 0 18px;overflow-x:auto;overflow-y:hidden;scrollbar-width:none;-ms-overflow-style:none}.tabs::-webkit-scrollbar{display:none}
.tabs a{padding:9px 14px;color:var(--mut);text-decoration:none;font-weight:500;border-bottom:2px solid transparent;margin-bottom:-1px;white-space:nowrap}
.tabs a:hover{color:var(--fg)}.tabs a.active{color:var(--acc);border-bottom-color:var(--acc)}
.codes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 18px;font:14px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:14px;border:1px dashed var(--bd2);border-radius:10px;background:var(--card2)}
.qr{background:#fff;border-radius:10px;padding:8px;display:inline-block;line-height:0}.qr svg{width:190px;height:190px}
fieldset{border:0;padding:0;margin:0;min-width:0}
@media (max-width:860px){.app{flex-direction:column}aside{display:none}.mobile-nav{display:flex;flex-direction:row;gap:4px;align-items:center;padding:10px 12px;border-bottom:1px solid var(--bd);background:var(--side);overflow-x:auto;position:sticky;top:0;z-index:5}
.mobile-nav a{padding:6px 10px;border-radius:8px;color:var(--mut);text-decoration:none;white-space:nowrap;font-weight:500}.mobile-nav a.active{background:var(--acc-soft);color:var(--acc)}
.topbar{padding:16px 16px 4px}main{padding:12px 16px 32px}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.row{flex-direction:column}.hide-sm{display:none}td[data-l]::before{content:attr(data-l) ": ";color:var(--mut)}
table,tbody,tr,td{display:block;width:100%}tr:first-child:has(th){display:none}tr{border-bottom:1px solid var(--bd);padding:8px 0}tr:last-child{border-bottom:0}td{border:0;padding:4px 10px;text-align:left!important;white-space:normal!important}td .btn{margin:2px 0}}
.taskbtn{position:relative}.taskbtn svg{width:16px;height:16px;vertical-align:-3px}.taskbtn .badge{margin-left:4px}.taskpop{position:fixed;top:70px;right:20px;width:min(640px,94vw);max-height:70vh;overflow:auto;z-index:90;background:var(--card);border:1px solid var(--bd);border-radius:12px;box-shadow:0 18px 50px rgba(0,0,0,.28);padding:14px 16px}.fm-task{display:flex;gap:10px;align-items:center;padding:8px 0;border-bottom:1px solid var(--bd)}.fm-task:last-child{border-bottom:0}.fm-bar{flex:0 0 120px;height:8px;background:var(--bd);border-radius:4px;overflow:hidden}.fm-bar i{display:block;height:100%}
</style></head><body>
{% set p = request.path %}

<nav class="mobile-nav"><a href="/dashboard" class="{{ 'active' if p.startswith('/dashboard') }}">Dashboard</a><a href="/" class="{{ 'active' if p == '/' or p.startswith('/job') }}">Aufgaben</a><a href="/schedules" class="{{ 'active' if p.startswith('/schedules') }}">Zeitpläne</a><a href="/remotes" class="{{ 'active' if p.startswith('/remotes') }}">Speicherorte</a>{% if can('files.view') %}<a href="/files" class="{{ 'active' if p.startswith('/files') }}">Dateien</a>{% endif %}{% if can('jobs.view') %}<a href="/stats" class="{{ 'active' if p.startswith('/stats') }}">Statistik</a>{% endif %}{% if can('system.audit') %}<a href="/audit" class="{{ 'active' if p.startswith('/audit') }}">Audit-Log</a>{% endif %}<a href="{{ '/users' if can('users.view') else ('/settings' if can('notify.view') else ('/settings/general' if can('system.settings') else ('/settings/access' if can('system.access') else '/account'))) }}" class="{{ 'active' if p.startswith(('/settings','/users','/account','/roles','/groups','/help')) }}">Einstellungen{% if fail_badge %} <span class="badge">{{ fail_badge }}</span>{% endif %}</a>{% if g.user %}<a href="/logout">Abmelden</a>{% endif %}</nav>
<div class="app">
<aside>
<div class="brand"><div class="logo">{{ ICON.jobs }}</div><span class="lbl">MirrorSync</span><button type="button" class="sidetog" id="sidetog" onclick="toggleSide()" title="{{ _('Seitenleiste ausklappen') if side_mini else _('Seitenleiste einklappen') }}" aria-label="{{ _('Seitenleiste ausklappen') if side_mini else _('Seitenleiste einklappen') }}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg></button></div>
<nav>
<a href="/dashboard" class="{{ 'active' if p.startswith('/dashboard') }}" title="Dashboard">{{ ICON.dash }}<span class="lbl">Dashboard</span></a>
<a href="/" class="{{ 'active' if p == '/' or p.startswith('/job') }}" title="Aufgaben">{{ ICON.jobs }}<span class="lbl">Aufgaben</span></a>
<a href="/schedules" class="{{ 'active' if p.startswith('/schedules') }}" title="Zeitpläne">{{ ICON.clock }}<span class="lbl">Zeitpläne</span></a>
<a href="/remotes" class="{{ 'active' if p.startswith('/remotes') }}" title="Speicherorte">{{ ICON.storage }}<span class="lbl">Speicherorte</span></a>
{% if can('files.view') %}<a href="/files" class="{{ 'active' if p.startswith('/files') }}" title="Dateien">{{ ICON.folder }}<span class="lbl">Dateien</span></a>{% endif %}
{% if can('jobs.view') %}<a href="/stats" class="{{ 'active' if p.startswith('/stats') }}" title="Statistik">{{ ICON.chart }}<span class="lbl">Statistik</span></a>{% endif %}
{% if can('system.audit') %}<a href="/audit" class="{{ 'active' if p.startswith('/audit') }}" title="Audit-Log">{{ ICON.audit }}<span class="lbl">Audit-Log</span></a>{% endif %}
<a href="{{ '/users' if can('users.view') else ('/settings' if can('notify.view') else ('/settings/general' if can('system.settings') else ('/settings/access' if can('system.access') else '/account'))) }}" class="{{ 'active' if p.startswith(('/settings','/users','/account','/roles','/groups','/help')) }}" title="Einstellungen">{{ ICON.gear }}<span class="lbl">Einstellungen</span>{% if fail_badge %}<span class="badge" title="unbestätigte Fehlversuche">{{ fail_badge }}</span>{% endif %}</a>
</nav>
<div class="side-foot">
<button type="button" onclick="toggleTheme()" title="Design wechseln">{{ ICON.theme }}<span id="themeLabel" class="lbl">Design wechseln</span></button>
{% if g.user %}<a href="/account" class="userchip" title="{{ g.user }}"><span class="avatar">{{ g.user[:1]|upper }}</span><span class="lbl"><b>{{ g.user }}</b><br><small>{{ role_name(g.role) }}</small></span></a>
<a href="/logout" title="Abmelden">{{ ICON.logout }}<span class="lbl">Abmelden</span></a>{% endif %}
<div class="ver"><a class="vlink" href="/changelog" title="Versionshinweise: was sich in jeder Version geändert hat">MirrorSync v{{ VERSION }}</a>{% set upd_s = UPDATE() %}{% if upd_s and upd_s.update_available %}<br><a class="upd" href="{{ upd_s.url }}" target="_blank" rel="noopener" title="Neue Version verfügbar">⬆ v{{ upd_s.latest }} verfügbar</a>{% if can("system.update") and SELFUPD_OK() %}<form method="post" action="/update/apply" style="margin:4px 0 0" onsubmit="return confirm('MirrorSync jetzt aktualisieren? Der Container wird dabei neu gestartet, die Oberfläche ist etwa eine Minute nicht erreichbar.')"><input type="hidden" name="back" value="{{ request.path }}"><button class="btn sm">Jetzt aktualisieren</button></form>{% endif %}{% endif %}</div>
</div>
</aside>
<div class="content">
<div class="topbar"><div><h1>{{ self.title() }}</h1>{% block subtitle %}{% endblock %}</div><div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">{% block actions %}{% endblock %}{% if g.user and (can('files.view') or can('jobs.view')) %}<button type="button" class="btn taskbtn" id="taskbtn" onclick="msTasksToggle(event)" title="Laufende Aufgaben sowie Kopier- und Verschiebe-Aufträge des Dateimanagers">{{ ICON.folder }} Aufträge <span class="badge" id="taskbadge" style="display:none">0</span></button>{% endif %}</div></div>
{% if g.user and (can('files.view') or can('jobs.view')) %}<div class="taskpop" id="taskpop" hidden>{% if can('jobs.view') %}<div id="jobrun"></div>{% endif %}{% if can('files.view') %}<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px"><b>Aufträge (Kopieren und Verschieben)</b><span style="flex:1"></span>{% if can("files.edit") %}<button type="button" class="btn sm" id="clrtasks" onclick="msTasksClear()">Alle fertigen entfernen</button>{% endif %}{% if not can('jobs.view') %}<button type="button" class="btn sm" onclick="msTasksToggle()" title="Schließen">✕</button>{% endif %}</div><div id="tasks"><div class="mut">Keine Aufträge.</div></div>{% endif %}</div>
<script>
(function(){const CAN_EDIT={{ 'true' if can("files.edit") else 'false' }},CAN_FILES={{ 'true' if can("files.view") else 'false' }},CAN_JOBS={{ 'true' if can("jobs.view") else 'false' }},CAN_RUN={{ 'true' if can("jobs.run") else 'false' }};let TT=null,wasRun=false,open=false;
const esc=t=>String(t??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const op=async(name,body)=>{try{const r=await fetch('/files/op/'+name,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(body||{})});return await r.json()}catch(e){return {ok:false}}};
const COL={'läuft':'var(--acc)','ok':'var(--ok)','fehler':'var(--err)','abgebrochen':'var(--mut)'};
const STT={'läuft':'läuft','ok':'fertig','fehler':'Fehler','abgebrochen':'abgebrochen'};
const msF=(x,...a)=>a.reduce((y,v,i)=>y.split('{'+i+'}').join(v),x);
const msB=window.msB=n=>{const u=['B','KB','MB','GB','TB'];let i=0;n=+n||0;while(n>=1024&&i<4){n/=1024;i++}return (i?n.toFixed(n<10?1:0):n)+' '+u[i]};
const msT=s=>{s=Math.round(+s||0);return s>=3600?Math.floor(s/3600)+' h '+Math.round(s%3600/60)+' min':s>=60?Math.floor(s/60)+' min '+(s%60)+' s':s+' s'};
/* Gesamtfortschritt eines Kopier-/Verschiebe-Auftrags als Text: Dateien x von y, Bytes, Tempo, Restzeit */
window.msTaskLine=t=>{const p=[];const run=t.state==='läuft';
  if(t.items>1&&run)p.push(msF('Eintrag {0} von {1}',t.item||1,t.items));
  if(t.files_total!=null)p.push(msF('{0} von {1} Dateien',t.files_done||0,t.files_total));else if(t.files_done)p.push(msF('{0} Dateien',t.files_done));
  if(t.bytes_total!=null)p.push(msB(t.bytes_done)+' '+'von'+' '+msB(t.bytes_total));else if(t.bytes_done)p.push(msB(t.bytes_done));
  if(run&&t.speed)p.push(msB(t.speed)+'/s');
  if(run&&t.eta!=null&&t.speed)p.push(msF('noch ca. {0}',msT(t.eta)));
  if(run&&t.bytes_total==null)p.push('Gesamtgröße wird ermittelt …');
  return p.join(' · ')};
async function jobsPoll(){if(!CAN_JOBS)return 0;let d;try{d=await (await fetch('/jobs/running',{headers:{'Accept':'application/json'}})).json()}catch(e){return 0}
  const el=document.getElementById('jobrun');if(!el||!d.ok)return 0;const L=d.jobs;
  el.innerHTML='<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px"><b>'+'Laufende Aufgaben'+'</b><span style="flex:1"></span>'+'<button type="button" class="btn sm" onclick="msTasksToggle()" title="'+'Schließen'+'">✕</button>'+'</div>'+
    (L.length?L.map(j=>'<div class="fm-task"><div style="flex:1;min-width:0"><a href="/job/'+esc(j.id)+'/log"><b>'+esc(j.name)+'</b></a>'+(j.live?' <small class="mut">⚡ Live</small>':'')+'<br><small class="mut">'+esc(j.path)+' · '+esc(j.started)+(j.stats?' · '+esc(j.stats):'')+'</small></div>'+
      '<span class="tag" style="color:var(--acc);white-space:nowrap">'+'läuft'+' · '+j.progress+' %</span><div class="fm-bar" title="'+j.progress+' %"><i style="width:'+j.progress+'%;background:var(--acc)"></i></div>'+
      (CAN_RUN?'<button type="button" class="btn sm del" data-js="'+esc(j.id)+'">'+'Stopp'+'</button>':'')+'</div>').join(''):'<div class="mut" style="padding:4px 0 10px">'+'Gerade läuft keine Aufgabe.'+'</div>')+(CAN_FILES?'<hr style="border:0;border-top:1px solid var(--bd);margin:8px 0 10px">':'');
  el.querySelectorAll('[data-js]').forEach(x=>x.onclick=async()=>{const f=new FormData();await fetch('/job/'+x.dataset.js+'/stop',{method:'POST',body:f});poll()});
  return L.length}
async function poll(){clearTimeout(TT);const jr=await jobsPoll();
  const d=CAN_FILES?await op('tasks'):{ok:true,tasks:[]};if(!d.ok){d.tasks=[]}
  const run=d.tasks.filter(t=>t.state==='läuft').length;const b=document.getElementById('taskbadge');b.textContent=run+jr;b.style.display=run+jr?'':'none';
  document.getElementById('taskbtn').classList.toggle('pri',run+jr>0);
  if(!CAN_FILES){TT=setTimeout(poll,jr?2000:(open?3000:10000));return}
  document.getElementById('tasks').innerHTML=d.tasks.length?d.tasks.map(t=>{const lab=t.op==='move'?'Verschieben':'Kopieren';const pc=t.state==='ok'?100:(t.progress||0);
    return '<div class="fm-task"><div style="flex:1;min-width:0"><b>'+esc(lab)+'</b> '+esc(t.label)+'<br><small class="mut">'+esc(t.started)+(msTaskLine(t)?' · '+esc(msTaskLine(t)):(t.stats&&t.state==='läuft'?' · '+esc(t.stats):''))+'</small>'+(t.error?'<br><small style="color:var(--err)">'+esc(t.error)+'</small>':'')+'</div>'+
      '<span class="tag" style="color:'+COL[t.state]+';white-space:nowrap">'+esc(STT[t.state]||t.state)+' · '+pc+' %</span>'+
      '<div class="fm-bar" title="'+pc+' %"><i style="width:'+pc+'%;background:'+COL[t.state]+'"></i></div>'+
      (CAN_EDIT?(t.state==='läuft'?'<button type="button" class="btn sm" data-c="'+t.id+'">'+'Abbrechen'+'</button>':'<button type="button" class="btn sm" data-r="'+t.id+'">'+'Entfernen'+'</button>'):'')+'</div>'}).join(''):'<div class="mut">'+'Keine Aufträge.'+'</div>';
  document.querySelectorAll('#tasks [data-c]').forEach(x=>x.onclick=async()=>{await op('cancel',{task_id:x.dataset.c});poll()});
  document.querySelectorAll('#tasks [data-r]').forEach(x=>x.onclick=async()=>{await op('remove_tasks',{task_id:x.dataset.r});poll()});
  const cb=document.getElementById('clrtasks');if(cb)cb.style.display=d.tasks.some(t=>t.state!=='läuft')?'':'none';
  if(window.onTasksUpdate)window.onTasksUpdate(d.tasks);
  if(wasRun&&!run&&window.onTasksDone)window.onTasksDone();wasRun=run>0;
  TT=setTimeout(poll,run?800:(jr?2000:(open?3000:10000)));}
window.msPoll=()=>{wasRun=true;poll()};
window.msTasksClear=async()=>{await op('remove_tasks',{finished:true});poll()};
const tpKeep=v=>{try{v?sessionStorage.setItem('ms_taskpop','1'):sessionStorage.removeItem('ms_taskpop')}catch(e){}};
window.msTasksToggle=(ev)=>{if(ev)ev.stopPropagation();const p=document.getElementById('taskpop');open=p.hidden;p.hidden=!open;tpKeep(open);if(open)poll()};
try{if(sessionStorage.getItem('ms_taskpop')==='1'){document.getElementById('taskpop').hidden=false;open=true}}catch(e){}
document.addEventListener('click',e=>{const p=document.getElementById('taskpop');if(!p.hidden&&e.target.isConnected&&!p.contains(e.target)&&!e.target.closest('#taskbtn,dialog')){p.hidden=true;open=false;tpKeep(false)}});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!document.querySelector('dialog[open]')){const p=document.getElementById('taskpop');if(!p.hidden){p.hidden=true;open=false;tpKeep(false)}}});
poll();})();
</script>{% endif %}
<main>{% set fl = session.pop('flash', None) %}{% if fl %}<div class="msg info">{{ fl }}</div>{% endif %}{% block body %}{% endblock %}</main>
</div></div>
<script>
// Pause- und Ändern-Menüs schließen, sobald man daneben klickt oder Esc drückt; immer nur eins offen
document.addEventListener('click',e=>{document.querySelectorAll('details.pausemenu[open]').forEach(d=>{if(!d.contains(e.target))d.removeAttribute('open')})});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('details.pausemenu[open]').forEach(d=>d.removeAttribute('open'))});
// Seitenleiste ein-/ausklappen: sofort umschalten, im Benutzerkonto merken (gilt auf allen Geräten)
function toggleSide(){const r=document.documentElement,mini=r.dataset.side!=='mini';if(mini)r.dataset.side='mini';else delete r.dataset.side;
const b=document.getElementById('sidetog');if(b){b.title=mini?'Seitenleiste ausklappen':'Seitenleiste einklappen';b.setAttribute('aria-label',b.title)}
const f=new FormData();f.append('state',mini?'mini':'full');fetch('/account/sidebar',{method:'POST',body:f,headers:{'Accept':'application/json'}}).catch(()=>{});
window.dispatchEvent(new Event('resize'))}
function toggleTheme(){const r=document.documentElement;const dark=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
r.dataset.theme=dark?'light':'dark';try{localStorage.setItem('ms-theme',r.dataset.theme)}catch(e){}}
if('serviceWorker' in navigator&&location.protocol!=='file:'){window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(()=>{}))}
</script>
{% set wn = WHATS_NEW() %}{% if wn %}<dialog id="whatsnew" class="wndlg"><div style="display:flex;align-items:center;gap:10px"><h3 style="margin:0;flex:1">🎉 {{ _("Neu in MirrorSync v{0}", VERSION) }}</h3><button type="button" class="btn sm" onclick="msSeen()">Schließen</button></div>
<div class="clbody" style="overflow:auto;max-height:62vh;margin-top:8px">{% for e in wn %}{% if wn|length > 1 %}<h3 style="margin:14px 0 2px">v{{ e.version }} <small class="mut">{{ e.date }}</small></h3>{% endif %}{{ e.html }}{% endfor %}</div>
<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:12px"><a class="btn" href="/changelog" onclick="msSeen(true)">Alle Versionshinweise</a><button type="button" class="btn pri" onclick="msSeen()">Verstanden</button></div></dialog>
<style>.wndlg{width:min(720px,94vw);max-height:88vh;border:1px solid var(--bd);border-radius:12px;background:var(--card);color:var(--fg);padding:18px 20px}.wndlg::backdrop{background:rgba(0,0,0,.35)}.clbody ul{margin:6px 0 10px;padding-left:20px}.clbody li{margin:3px 0}.clbody p{margin:8px 0}.clbody h4{margin:12px 0 4px}</style>
<script>function msSeen(nav){fetch('/changelog/seen',{method:'POST',headers:{'Accept':'application/json'},keepalive:true}).catch(()=>{});if(!nav)document.getElementById('whatsnew').close()}
(function(){const d=document.getElementById('whatsnew');if(d&&d.showModal){d.addEventListener('cancel',()=>msSeen(true));d.showModal()}})()</script>{% endif %}
</body></html>
""",

"index.html": r"""{% extends "base.html" %}{% block title %}Aufgaben{% endblock %}
{% block subtitle %}<p>Spiegel-Aufgaben: Das Ziel wird exakt wie die Quelle.</p>{% endblock %}
{% block actions %}{% if can("jobs.create") %}<a class="btn pri" href="/job/new">{{ ICON.plus }} Neue Aufgabe</a>{% endif %}{% endblock %}
{% block body %}
<div class="stats">
<div class="stat"><div class="k">Aufgaben</div><div class="v">{{ jobs|length }}</div></div>
<div class="stat"><div class="k">Automatisch</div><div class="v">{{ jobs|rejectattr('is_paused')|selectattr('trig','equalto','time')|selectattr('next_run')|list|length + jobs|rejectattr('is_paused')|selectattr('trig','in',['after','live'])|selectattr('enabled')|list|length }}</div></div>
{% set np = jobs|selectattr('is_paused')|list|length %}{% if np %}<div class="stat"><div class="k">Pausiert</div><div class="v">{{ np }}</div></div>{% endif %}
<div class="stat"><div class="k">Laufen gerade</div><div class="v laeuft">{{ jobs|selectattr('running')|list|length }}</div></div>
<div class="stat"><div class="k">Letzter Lauf fehlgeschlagen</div><div class="v {{ 'fehler' if jobs|selectattr('last_status','equalto','fehler')|list }}">{{ jobs|selectattr('last_status','equalto','fehler')|list|length }}</div></div>
</div>
<div class="card" style="padding:6px 8px">
{% if not jobs %}<div class="empty"><p style="font-size:15px;color:var(--fg);margin-bottom:4px">Noch keine Aufgaben</p>
<p>Lege zuerst unter <a href="/remotes">Speicherorte</a> deine Server an, dann eine Aufgabe.</p>
{% if can("jobs.create") %}<p><a class="btn pri" href="/job/new">{{ ICON.plus }} Neue Aufgabe</a></p>{% endif %}</div>
{% else %}<table><tr><th>Aufgabe</th><th class="hide-sm">Zeitplan</th><th>Status</th><th style="text-align:right">Aktionen</th></tr>
{% for j in jobs %}<tr class="{{ 'paused' if j.is_paused }}">
<td style="{{ 'padding-left:%dpx' % (10 + 22 * j.depth) if j.depth }}">{% if j.depth %}<span class="chain">↳</span>{% endif %}<a href="/job/{{ j.id }}" style="color:inherit;text-decoration:none"><span class="jobname">{{ j.name }}</span></a>{% if j.is_paused %} <span class="tag pausetag" title="{{ 'von ' ~ j.paused_by if j.paused_by }}">{{ j.pause_text }}</span>{% endif %}
<div class="path">{% if j.direction == "bisync" %}<span title="Zwei-Wege-Sync">{{ j.source }} ⇄ {{ j.eff_dest }}</span>{% else %}{{ j.source }} → {{ j.eff_dest }}{% endif %}</div>
{% if j.direction == "bisync" and j.bisync_need_resync %}<small class="fehler">Zwei-Wege-Sync abgebrochen, bitte neu zusammenführen.</small>
{% if can("jobs.run") and not j.running %}<form class="inline" method="post" action="/job/{{ j.id }}/resync" onsubmit="return confirm('Beide Seiten neu zusammenführen? Was nur auf einer Seite liegt, wird auf die andere kopiert. Gelöscht wird nichts.')"><button class="btn sm">Neu zusammenführen</button></form>{% endif %}<br>{% endif %}
{% if j.delete_hold %}{% set h = j.delete_hold %}<div class="msg err" style="margin:6px 0;padding:8px 10px"><b>🛑 Angehalten: Löschwarnung</b><br><small>{{ _("{0} von {1} Dateien im Ziel würden gelöscht ({2} %, Grenze {3} %).", h.deleted, h.total, h.pct, h.threshold) }}</small>
{% if can("jobs.approve") and not j.running %}<div style="margin-top:6px"><form class="inline" method="post" action="/job/{{ j.id }}/approve" data-q="{{ _('Wirklich freigeben? Der Lauf startet jetzt und löscht {0} Dateien im Ziel.', h.deleted) }}" onsubmit="return confirm(this.dataset.q)"><button class="btn sm del">Freigeben und spiegeln</button></form> <form class="inline" method="post" action="/job/{{ j.id }}/hold/dismiss"><button class="btn sm">Warnung verwerfen</button></form> <a class="btn sm" href="/job/{{ j.id }}/log">Details</a></div>{% endif %}</div>{% endif %}
{% if j.retry_pending and not j.running %}<small class="mut" title="Nach einem Fehler">↻ {{ _("neuer Versuch {0} von {1} um {2}", j.retry_pending.attempt, j.retry_pending.of, j.retry_pending.at[11:16]) }}</small><br>{% endif %}
<small>{% if j.direction == "bisync" %}⇄ Zwei-Wege · {% endif %}{% if j.n_select %}☑ nur {{ j.n_select }} {{ "Eintrag" if j.n_select == 1 else "Einträge" }} · {% endif %}{% if j.n_excludes %}{{ j.n_excludes }} Ausschlüsse · {% endif %}{% if j.no_delete and j.direction != "bisync" %}ohne Löschen · {% endif %}{% if j.versioning %}Versionierung · {% endif %}{% if j.encrypt and j.direction != "bisync" %}<span title="Ziel verschlüsselt (rclone crypt)">🔒 verschlüsselt</span> · {% endif %}{% if j.verify and j.verify != "off" %}🔎 Prüflauf · {% endif %}{% if j.delete_guard and j.direction != "bisync" %}🛡 Löschwarnung ab {{ j.delete_guard }} % · {% endif %}{% if j.retry %}↻ Wiederholen · {% endif %}{% if j.wol_mac %}⏰ Wake-on-LAN · {% endif %}{% if j.snapshot and j.snapshot != "off" %}📸 Snapshot · {% endif %}{% if j.window_text %}🕘 {{ j.window_text }} · {% endif %}{% if j.notify_summary %}🔔 {{ j.notify_summary }}{% endif %}{% if j.dry_run %} · nur Testlauf{% endif %}</small></td>
<td class="hide-sm">{% if j.trig == "after" %}{% if j.parent_name %}<span title="startet nach einer anderen Aufgabe">⛓ nach „{{ j.parent_name }}“</span><br><small>{{ "immer" if j.after_when == "always" else "nur bei Erfolg" }}{% if not j.enabled %} · <span class="fehler">aus</span>{% endif %}</small>{% else %}<span class="fehler">Vorgänger fehlt</span>{% endif %}
{% elif j.trig == "time" and j.enabled and j.next_run %}{% if j.schedule_text %}{{ j.schedule_text }}{% else %}<code>{{ j.schedule }}</code>{% endif %}
{% elif j.trig == "live" and j.enabled %}<span title="gleicht laufend Quelle und Ziel ab">⚡ {{ j.live_text }}</span><br><small>{{ j.live_full_text }}{% if j.next_run %}, nächster {{ j.next_run }}{% endif %}</small>{% if j.live_fail_count %}<br><small class="fehler">{{ j.live_fail_count }} Live-Läufe in Folge fehlgeschlagen</small>{% elif j.live_checked %}<br><small class="mut">zuletzt geprüft {{ j.live_checked[11:16] }}</small>{% endif %}
{% elif j.trig == "live" %}<small>Live aus</small>
{% elif j.trig == "time" %}<small>Zeitplan aus</small>{% else %}<small>manuell</small>{% endif %}
{% if j.followers %}<br><small class="mut">danach: {{ j.followers|join(", ") }}</small>{% endif %}</td>
<td>{% if j.running %}<span class="tag laeuft">läuft</span>{% elif j.last_status %}<span class="tag {{ j.last_status }}">{{ STATUS.get(j.last_status, j.last_status) }}</span><br><small>{{ j.last_run }}</small>{% else %}<span class="tag">noch nie</span>{% endif %}
{% set w %}{% if j.next_day == 0 %}{{ _("heute, {0}", j.next_hm) }}{% elif j.next_day == 1 %}{{ _("morgen, {0}", j.next_hm) }}{% else %}{{ j.next_full }}{% endif %}{% endset %}
<div class="nextrun"><small class="mut">{{ _("Nächster Lauf") }}:</small> {% if j.next_at and j.next_kind == "after" %}<small title="{{ _('geschätzt: startet nach „{0}“', j.parent_name) }}"><b>{{ _("ca. {0}", w) }}</b></small>
{% elif j.next_at %}<small><b>{{ w }}</b></small>
{% elif j.next_kind == "parent_running" %}<small>{{ _("wenn „{0}“ fertig ist", j.parent_name) }}</small>
{% elif j.next_kind == "manual" %}<small class="mut">{{ _("nur manuell") }}</small>
{% elif j.next_kind == "paused" %}<small class="mut">{{ _("pausiert") }}</small>
{% else %}<small class="mut">{{ _("keiner geplant") }}</small>{% endif %}{% if j.window_open and not j.running %}<br><span class="tag" title="Startet automatisch, sobald das Zeitfenster aufgeht">🕘 <span>wartet auf Zeitfenster</span> ({{ j.window_open }})</span>{% endif %}</div></td>
<td style="text-align:right;white-space:nowrap">
{% if j.running %}{% if can("jobs.run") %}<form class="inline" method="post" action="/job/{{ j.id }}/stop"><button class="btn sm del">Stopp</button></form>{% endif %}
{% else %}{% if can("jobs.run") %}<form class="inline" method="post" action="/job/{{ j.id }}/run"><button class="btn sm pri" title="Jetzt spiegeln">{{ ICON.play }} Start</button></form>{% endif %}
{% if can("jobs.dryrun") %}<form class="inline" method="post" action="/job/{{ j.id }}/run"><input type="hidden" name="dry" value="1"><button class="btn sm" title="Testlauf: zeigt nur, was passieren würde">Test</button></form>{% endif %}{% endif %}
{% if can("jobs.edit") %}{% if j.is_paused %}<form class="inline" method="post" action="/job/{{ j.id }}/pause"><input type="hidden" name="action" value="resume"><button class="btn sm" title="Pause beenden">▶ Fortsetzen</button></form>
{% else %}<details class="pausemenu"><summary class="btn sm" title="Pausieren: startet nicht per Zeitplan, Live oder Kette">Pause</summary><div class="pmenu">
<b>Pausieren</b>
<form method="post" action="/job/{{ j.id }}/pause"><button class="btn sm">bis ich fortsetze</button></form>
<form method="post" action="/job/{{ j.id }}/pause"><input type="hidden" name="hours" value="1"><button class="btn sm">1 Stunde</button></form>
<form method="post" action="/job/{{ j.id }}/pause"><input type="hidden" name="hours" value="24"><button class="btn sm">24 Stunden</button></form>
<form method="post" action="/job/{{ j.id }}/pause"><input type="hidden" name="hours" value="168"><button class="btn sm">1 Woche</button></form>
<form method="post" action="/job/{{ j.id }}/pause" class="pdate"><input type="datetime-local" name="until" required><button class="btn sm pri">bis</button></form>
</div></details>{% endif %}{% endif %}
{% if can("jobs.logs") %}<a class="btn sm" href="/job/{{ j.id }}/log">Log</a>{% endif %} <a class="btn sm" href="/job/{{ j.id }}">{{ "Bearbeiten" if can("jobs.edit") else "Ansehen" }}</a>{% if can("jobs.create") %}<form class="inline" method="post" action="/job/{{ j.id }}/duplicate"><button class="btn sm" title="Duplizieren: Kopie dieser Aufgabe anlegen (ausgeschaltet)" aria-label="Duplizieren">⧉</button></form>{% endif %}
{% if can("jobs.delete") %}<form class="inline" method="post" action="/job/{{ j.id }}/delete" data-q="{{ _('Aufgabe „{0}“ wirklich entfernen? Die Dateien in Quelle und Ziel bleiben unberührt.', j.name) }}" onsubmit="return confirm(this.dataset.q)"><button class="btn sm del" title="Aufgabe entfernen">Entfernen</button></form>{% endif %}</td>
</tr>{% endfor %}</table>{% endif %}
</div>
{% endblock %}
""",

"job.html": r"""{% extends "base.html" %}{% block title %}{{ job.name if job_id else "Neue Aufgabe" }}{% endblock %}
{% block subtitle %}<p>{{ "Aufgabe bearbeiten" if job_id else "Neue Spiegel-Aufgabe anlegen" }}</p>{% endblock %}
{% block actions %}<a class="btn" href="/help#job" title="Hilfe: alle Einstellungen der Aufgabe erklärt">❓ Hilfe</a> {% if job_id %}{% if can("jobs.create") %}<form class="inline" method="post" action="/job/{{ job_id }}/duplicate"><button class="btn" title="Kopie dieser Aufgabe anlegen (ausgeschaltet)">⧉ Duplizieren</button></form> {% endif %}<a class="btn" href="/job/{{ job_id }}/log">Log</a>{% endif %}{% endblock %}
{% block body %}
{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}
{% if error %}<div class="msg err">{{ error }}</div>{% endif %}
{% set editable = (can("jobs.edit") if job_id else can("jobs.create")) %}{% if not editable %}<div class="msg info">Nur ansehen: Deine Rolle darf diese Aufgabe nicht ändern.</div>{% endif %}
<aside class="fbpanel" id="fbpanel" aria-hidden="true">
<div class="fbtop"><b id="fbtitle">Durchsuchen</b><span style="flex:1"></span><input type="text" id="fbq" placeholder="Im Ordner suchen" autocomplete="off"><button type="button" class="btn sm" onclick="FB.path!==null&&fbLoad(FB.path)" title="Neu laden">↻</button><button type="button" class="btn sm" onclick="closeFB()" title="Schließen (Esc)">✕</button></div>
<div class="fbcrumbs" id="fbcrumbs"></div><div id="fbmsg"></div>
<div class="fbtable"><table id="fbt"><thead id="fbhead"><tr><th data-k="name">Name</th><th data-k="size" class="num hide-sm">Größe</th><th data-k="mod" class="hide-sm">Geändert</th></tr></thead><tbody id="fbbody"></tbody></table></div>
<div class="fbfoot" id="fbfoot"><span class="hint" id="fbsum"></span><span style="flex:1"></span><button type="button" class="btn pri fbuse" onclick="fbUse()">Übernehmen</button></div>
</aside><div class="fbshade" onclick="closeFB()"></div>
<form method="post" id="jobform"><fieldset {{ "disabled" if not editable }}>
<div class="card"><h2>Art der Aufgabe</h2>
{% set tw_locked = not can("jobs.twoway") %}
<div class="seg" id="dirseg" style="flex-wrap:wrap">
<label><input type="radio" name="direction" value="mirror" {{ "checked" if job.direction != "bisync" }} onchange="dirShow()" {{ "disabled" if tw_locked and job.direction == "bisync" }}><span>➡ Spiegeln (Einweg): Quelle → Ziel</span></label>
<label><input type="radio" name="direction" value="bisync" {{ "checked" if job.direction == "bisync" }} onchange="dirShow()" {{ "disabled" if tw_locked and job.direction != "bisync" }}><span>⇄ Zwei-Wege-Sync: Seite A ⇄ Seite B</span></label></div>
<div class="hint ow-only">Das Ziel wird an die Quelle angeglichen. In der Quelle wird nie etwas verändert.</div>
<div class="hint tw-only">Änderungen auf beiden Seiten werden auf die jeweils andere übertragen, auch Löschungen. Beide Seiten werden also beschrieben.{% if tw_locked %} Zum Umstellen fehlt dir das Recht „Zwei-Wege-Sync einrichten“.{% endif %}</div>
{% if tw_locked and job.direction == "bisync" %}<input type="hidden" name="direction" value="bisync">{% endif %}
</div>
<div class="card"><h2 id="h_sd">Quelle und Ziel</h2>
<label>Name</label><input type="text" name="name" value="{{ job.name }}" required>
<label id="lbl_src">Quelle</label>
<div class="row" style="flex-direction:row"><input type="text" id="source" name="source" value="{{ job.source }}" placeholder="server-a:/var/www  oder  /data/daten/fotos" required>
<button type="button" class="btn" style="flex:0 0 auto{{ ';display:none' if not can('remotes.browse') }}" onclick="openFB('source')">Durchsuchen</button></div>
<div>
<label>Nur diese Dateien und Ordner <span class="mut" style="font-weight:normal">(leer = der ganze Quellordner)</span></label>
<textarea name="selection" id="selection" rows="3" placeholder="leer lassen, um den ganzen Quellordner zu spiegeln&#10;Projekte/&#10;bericht.docx">{{ job.selection or "" }}</textarea>
<div class="hint">Ein Eintrag pro Zeile, relativ zur Quelle, Ordner mit <code>/</code> am Ende. Im Browser setzt du dafür Häkchen an Ordner und Dateien.
Dann wird nur die Auswahl geprüft und gespiegelt, im Ziel wird nur innerhalb der Auswahl gelöscht. Trägst du als Quelle direkt eine Datei ein, wird das beim Speichern automatisch zu Ordner + Auswahl.
<a href="#" id="selclear" onclick="event.preventDefault();fbEl('selection').value='';destPreview()">Auswahl leeren</a></div>
<div class="hint tw-only">Beim Zwei-Wege-Sync gilt die Auswahl für beide Seiten: Nur die gewählten Ordner und Dateien werden in beide Richtungen abgeglichen, alles andere bleibt auf beiden Seiten unberührt.</div>
</div>
<label id="lbl_dst">Ziel (wird an die Quelle angeglichen)</label>
<div class="row" style="flex-direction:row"><input type="text" id="dest" name="dest" value="{{ job.dest }}" placeholder="server-b:backup/www" required>
<button type="button" class="btn" style="flex:0 0 auto{{ ';display:none' if not can('remotes.browse') }}" onclick="openFB('dest')">Durchsuchen</button></div>
<div class="hint">Entfernte Speicher: <code>name:pfad</code>. Lokale Ordner: <code>/data/…</code>.
Vorhanden: {% for r in remotes %}<code>{{ r.name }}:</code> ({{ r.type }}) {% else %}noch keine, siehe <a href="/remotes">Speicherorte</a>{% endfor %}</div>
<div>
<label class="check" style="margin-top:14px"><input type="checkbox" name="include_source_dir" id="incdir" {{ "checked" if job.include_source_dir }} onchange="destPreview()"> Quellordner selbst mitkopieren (im Ziel wird ein Ordner mit dem Namen der Quelle angelegt)</label>
<div class="hint" id="incoff" style="display:none">Bei einer Auswahl aus: Die gewählten Ordner und Dateien landen direkt im Ziel, ohne den Quellordner darüber.</div>
<div class="hint" id="destprev"></div>
{% if can("jobs.preview") %}<p style="margin:10px 0 0"><button type="button" class="btn" onclick="pvOpen()">🗂 Vorschau der Ordnerstruktur</button> <button type="submit" form="jobform" class="btn" formaction="{{ "/job/" ~ job_id ~ "/preview/page" if job_id else "/job/preview/page" }}" formmethod="post" formtarget="_blank" formnovalidate>📂 Ergebnis im Browser öffnen</button> <span class="hint" style="display:inline">Zeigt, wie das Ziel nach dem nächsten Lauf aussieht. Es wird nichts kopiert oder gelöscht.</span></p>
<dialog id="pvdlg" class="pvdlg"><div style="display:flex;align-items:center;gap:10px"><h3 style="margin:0;flex:1">Vorschau der Ordnerstruktur</h3><button type="button" class="btn sm" onclick="document.getElementById('pvdlg').close()">Schließen</button></div>
<div id="pvbody" style="margin-top:12px"></div></dialog>
<style>.pvdlg{width:min(980px,96vw);max-height:88vh;border:1px solid var(--bd);border-radius:12px;background:var(--card);color:var(--fg);padding:18px 20px}.pvdlg::backdrop{background:rgba(0,0,0,.35)}.pvt{font-size:14px;line-height:1.7}.pvt ul{list-style:none;margin:0;padding-left:18px}.pvt>ul{padding-left:0}.pvt summary{cursor:pointer}.pvt .pf{white-space:nowrap}
.pvt .s-new{color:var(--ok)}.pvt .s-update{color:var(--run,#2563eb)}.pvt .s-delete{color:var(--err);text-decoration:line-through}.pvt .s-to_a{color:var(--warn,#d97706)}
.pvt .cnt{font-size:12px;color:var(--mut);margin-left:6px}.pvleg span{margin-right:14px;white-space:nowrap}
.pvbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0 0 8px}.pvbar input[type=text]{height:32px;width:min(220px,50vw)}
.pvseg{display:inline-flex;border:1px solid var(--bd);border-radius:8px;overflow:hidden}.pvseg button{border:0;background:transparent;color:var(--fg);font:inherit;font-size:13px;padding:5px 12px;cursor:pointer}.pvseg button.on{background:var(--acc-soft);font-weight:600}
.pvb .fbcrumbs{margin:0 0 6px}.pvb .fbtable{max-height:56vh}.pvb table{width:100%}.pvb th{position:sticky;top:0;background:var(--card);z-index:1;text-align:left}.pvb td{padding:6px 10px}.pvb .num{text-align:right;white-space:nowrap}
.pvb tr.fdir a{text-decoration:none;color:var(--fg);font-weight:500}.pvb tr.s-delete td:first-child{text-decoration:line-through;opacity:.75}
.pvb .st{font-size:12px;white-space:nowrap}.pvb .st.s-new{color:var(--ok)}.pvb .st.s-update{color:var(--run,#2563eb)}.pvb .st.s-delete{color:var(--err)}.pvb .st.s-to_a{color:var(--warn,#d97706)}
.pvb tr.s-new td:first-child{box-shadow:inset 3px 0 0 var(--ok)}.pvb tr.s-update td:first-child{box-shadow:inset 3px 0 0 var(--run,#2563eb)}.pvb tr.s-delete td:first-child{box-shadow:inset 3px 0 0 var(--err)}.pvb tr.s-to_a td:first-child{box-shadow:inset 3px 0 0 var(--warn,#d97706)}
.pvb .cnt{font-size:12px;color:var(--mut);margin-left:6px}@media(max-width:700px){.pvb .hide-sm{display:none}}</style>
{% include "pv_up.html" %}<script>
function pvEsc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function pvSize(b){const u=['B','KB','MB','GB','TB'];let i=0;while(b>=1024&&i<4){b/=1024;i++}return (i?b.toFixed(1):b)+' '+u[i]}
const PV_LABEL={new:'neu',update:'wird aktualisiert',delete:'wird gelöscht',to_a:'kommt nach A',same:''};
function pvCnt(c){const p=[];if(c.new)p.push('+'+c.new);if(c.update)p.push('~'+c.update);if(c.delete)p.push('−'+c.delete);if(c.to_a)p.push('←'+c.to_a);const t=c.new+c.update+c.same+c.to_a;return p.length?'<span class="cnt">'+p.join(' ')+(t?' · '+t+' '+'Dateien':'')+'</span>':(c.same?'<span class="cnt">'+c.same+' '+'Dateien'+'</span>':'')}
function pvNode(n,depth){
 if(!n.d){const lab=PV_LABEL[n.s]?' <span class="cnt">'+PV_LABEL[n.s]+'</span>':'';return '<li class="pf s-'+n.s+'">📄 '+pvEsc(n.n)+' <span class="cnt">'+pvSize(n.size||0)+'</span>'+lab+'</li>'}
 const lab=(n.s!=='same'&&PV_LABEL[n.s])?' <span class="cnt">'+PV_LABEL[n.s]+'</span>':'';
 const kids=n.ch&&n.ch.length?'<ul>'+n.ch.map(k=>pvNode(k,depth+1)).join('')+'</ul>':'';
 return '<li><details'+(depth<1?' open':'')+'><summary class="s-'+n.s+'">📁 '+pvEsc(n.n)+'/'+lab+pvCnt(n.c)+'</summary>'+kids+'</details></li>'}
async function pvOpen(){const d=document.getElementById('pvdlg'),b=document.getElementById('pvbody');b.innerHTML='<p class="mut">'+'Quelle und Ziel werden gelesen …'+'</p>';d.showModal();
 try{const r=await fetch('{{ "/job/" ~ job_id ~ "/preview" if job_id else "/job/preview" }}',{method:'POST',body:new FormData(document.getElementById('jobform')),headers:{Accept:'application/json'}});
  const j=await r.json();if(!j.ok){b.innerHTML='<div class="msg err">'+pvEsc(j.error||r.status)+'</div>';return}
  const f=j.summary.files,y=j.summary.bytes;
  let h='<p style="margin:0 0 6px"><span class="mut">'+'Ziel'+':</span> <code>'+pvEsc(j.dest)+'</code>'+(j.dest_missing?' <span class="tag">'+'wird angelegt'+'</span>':'')+'</p>';
  h+='<p class="pvleg" style="margin:0 0 10px"><span class="s-new">+ '+f.new+' '+'neu'+' ('+pvSize(y.new)+')</span><span class="s-update">~ '+f.update+' '+'werden aktualisiert'+'</span><span class="s-delete">− '+f.delete+' '+'werden gelöscht'+'</span>'+(j.mode==='bisync'?'<span class="s-to_a">← '+f.to_a+' '+'kommen nach A'+'</span>':'')+'<span class="mut">'+f.same+' '+'bleiben gleich'+'</span></p>';
  if(j.mode==='bisync')h+='<div class="hint" style="margin-bottom:8px">'+'Zwei-Wege: So sehen danach beide Seiten aus. Gezeigt ist der Stand ohne Löschungen, die seit dem letzten Lauf auf einer Seite passiert sind.'+'</div>';
  if(j.truncated)h+='<div class="hint" style="margin-bottom:8px">'+'Sehr viele Dateien: Einzeln gezeigt werden nur die ersten Dateien, die Zähler an den Ordnern stimmen trotzdem.'+'</div>';
  PV.data=j;PV.path=[];PV.up=null;PV.ds=PVUP.split(j.dest);
  if(!(j.tree.ch||[]).length){b.innerHTML=h+'<p class="mut">'+'Nach dem Lauf ist das Ziel leer.'+'</p>';return}
  h+='<div class="pvbar"><span class="pvseg"><button type="button" data-v="result" onclick="pvSetView(\'result\')" title="'+'So sieht das Ziel nach dem Lauf aus. Was gelöscht wird, ist nicht mehr zu sehen.'+'">'+'✅ Ergebnis'+'</button><button type="button" data-v="browse" onclick="pvSetView(\'browse\')" title="'+'Zeigt, was sich ändert: neu, wird aktualisiert, wird gelöscht.'+'">'+'📂 Änderungen'+'</button><button type="button" data-v="tree" onclick="pvSetView(\'tree\')">'+'🌳 Baum'+'</button></span>'+
   '<label class="check" id="pvonlyl" style="margin:0"><input type="checkbox" id="pvonly" onchange="pvRender()"> '+'Nur Änderungen zeigen'+'</label><span style="flex:1"></span>'+
   '<button type="submit" form="jobform" class="btn sm" formaction="{{ "/job/" ~ job_id ~ "/preview/page" if job_id else "/job/preview/page" }}" formmethod="post" formtarget="_blank" formnovalidate>'+'📂 Im Browser öffnen'+'</button>'+
   '<input type="text" id="pvq" placeholder="'+'Im Ordner suchen'+'" autocomplete="off" oninput="pvRender()"></div><div id="pvview"></div>';
  b.innerHTML=h;pvRender()}catch(e){b.innerHTML='<div class="msg err">'+pvEsc(e.message||e)+'</div>'}}
const PV={data:null,path:[],view:'result'};try{PV.view=localStorage.getItem('pvView')||'result'}catch(e){}
function pvResult(n){if(!n.d)return n;const c=Object.assign({},n.c),b=Object.assign({},n.b);c.delete=0;b.delete=0;return Object.assign({},n,{c,b,ch:n.ch.filter(k=>k.s!=='delete').map(pvResult)})}
function pvSetView(v){PV.view=v;try{localStorage.setItem('pvView',v)}catch(e){}pvRender()}
function pvChanged(n){return n.s!=='same'||(n.d&&(n.c.new+n.c.update+n.c.delete+n.c.to_a)>0)}
function pvPrune(n){if(!n.d)return n;return Object.assign({},n,{ch:n.ch.filter(pvChanged).map(pvPrune)})}
function pvDate(s){return s?s.slice(8,10)+'.'+s.slice(5,7)+'.'+s.slice(0,4)+' '+s.slice(11,16):''}
function pvAbs(){return PV.up!==null?PV.up:PV.ds.segs.concat(PV.path)}
function pvSet(abs){const d=PV.ds.segs;if(PVUP.isPrefix(d,abs)){PV.up=null;PV.path=abs.slice(d.length)}else PV.up=abs;document.getElementById('pvq').value='';pvRender()}
function pvGo(i){pvSet(pvAbs().slice(0,i))}
function pvUp(){const a=pvAbs();if(a.length&&(PV.up!==null||PV.path.length||PVUP.can))pvSet(a.slice(0,-1))}
async function pvRenderUp(v,res){const up=PV.up,my=PV.req=(PV.req||0)+1;v.innerHTML='<div class="pvb">'+pvCrumb()+'<div class="hint" style="padding:10px">'+'Lade…'+'</div></div>';
 const r=await PVUP.list(PVUP.join(PV.ds.base,up));if(my!==PV.req)return;const r2=PVUP.onWay(r,up,PV.ds.segs);
 if(r2.ok===false){v.innerHTML='<div class="pvb">'+pvCrumb()+'<div class="msg err">'+pvEsc(r.error||'Fehler')+'</div></div>';return}
 const f=document.getElementById('pvq').value.trim().toLowerCase(),rows=PVUP.rows(r2,up,PV.ds.segs).filter(k=>!f||k.n.toLowerCase().includes(f));
 let t='<div class="hint" style="margin:0 0 6px">'+PVUP.note+'</div><div class="fbtable"><table><thead><tr><th>'+'Name'+'</th>'+(res?'':'<th>'+'Änderung'+'</th>')+'<th class="num hide-sm">'+'Größe'+'</th><th class="hide-sm">'+'Geändert'+'</th></tr></thead><tbody>';
 if(up.length)t+='<tr class="fdir"><td colspan="4"><a href="#" onclick="pvUp();return false">⬆ ..</a></td></tr>';
 rows.forEach((k,i)=>{t+='<tr class="'+(k.d?'fdir':'ffile')+'"><td>'+(k.d?'<a href="#" data-i="'+i+'">📁 '+pvEsc(k.n)+'</a>':'📄 '+pvEsc(k.n))+PVUP.tag(k)+'</td>'+(res?'':'<td></td>')+'<td class="num hide-sm">'+(k.d||k.size==null?'':pvSize(k.size))+'</td><td class="hide-sm"><small>'+pvEsc(k.mod?pvDate(k.mod.replace(' ','T')):'')+'</small></td></tr>'});
 if(!rows.length)t+='<tr><td colspan="4" class="mut" style="padding:14px">'+'Ordner ist leer.'+'</td></tr>';
 v.innerHTML='<div class="pvb">'+pvCrumb()+t+'</tbody></table></div></div>';
 v.querySelectorAll('a[data-i]').forEach(a=>a.onclick=e=>{e.preventDefault();pvSet(up.concat([rows[+a.dataset.i].n]))})}
function pvCrumb(){const a=pvAbs(),dl=PV.ds.segs.length;let c='<div class="fbcrumbs"><a href="#" onclick="pvGo(0);return false">'+pvEsc(PV.ds.base)+'</a>';
 a.forEach((p,i)=>{c+=(i?'<span class="sep">›</span>':'')+(i===a.length-1?'<b>'+pvEsc(p)+'</b>':'<a href="#" onclick="pvGo('+(i+1)+');return false">'+pvEsc(p)+'</a>')+(i===dl-1?' 🎯':'')});return c+'</div>'}
function pvInto(name){pvSet(pvAbs().concat([name]))}
function pvRender(){const v=document.getElementById('pvview');if(!v||!PV.data)return;
 document.querySelectorAll('.pvseg button').forEach(x=>x.classList.toggle('on',x.dataset.v===PV.view));
 const res=PV.view==='result',q=document.getElementById('pvq');document.getElementById('pvonlyl').style.display=res?'none':'';
 const only=!res&&document.getElementById('pvonly').checked;q.style.display=PV.view!=='tree'?'':'none';
 const root=res?pvResult(PV.data.tree):only?pvPrune(PV.data.tree):PV.data.tree;
 if(PV.view==='tree'){const kids=root.ch||[];v.innerHTML=kids.length?'<div class="pvt"><ul>'+kids.map(k=>pvNode(k,0)).join('')+'</ul></div>':'<p class="mut">'+'Keine Änderungen.'+'</p>';return}
 if(PV.up!==null){pvRenderUp(v,res);return}
 let node=root,ok=[];for(const p of PV.path){const k=(node.ch||[]).find(x=>x.d&&x.n===p);if(!k)break;node=k;ok.push(p)}PV.path=ok;
 const c=pvCrumb();
 const f=q.value.trim().toLowerCase();const rows=(node.ch||[]).filter(k=>!f||k.n.toLowerCase().includes(f));
 let t='<div class="fbtable"><table><thead><tr><th>'+'Name'+'</th>'+(res?'':'<th>'+'Änderung'+'</th>')+'<th class="num hide-sm">'+'Größe'+'</th><th class="hide-sm">'+'Geändert'+'</th></tr></thead><tbody>';
 if(PV.path.length||(PVUP.can&&PV.ds.segs.length))t+='<tr class="fdir"><td colspan="4"><a href="#" onclick="pvUp();return false">⬆ ..</a></td></tr>';
 if(res){rows.forEach((k,i)=>{if(k.d){const b=k.b,sz=b.new+b.update+b.same+b.to_a;t+='<tr class="fdir"><td><a href="#" data-i="'+i+'">📁 '+pvEsc(k.n)+'</a></td><td class="num hide-sm">'+(sz?pvSize(sz):'')+'</td><td class="hide-sm"></td></tr>'}
  else t+='<tr class="ffile"><td>📄 '+pvEsc(k.n)+'</td><td class="num hide-sm">'+pvSize(k.size||0)+'</td><td class="hide-sm"><small>'+pvDate(k.m)+'</small></td></tr>'});
  if(!rows.length)t+='<tr><td colspan="3" class="mut" style="padding:14px">'+'Ordner ist leer.'+'</td></tr>'}else{
 rows.forEach((k,i)=>{const lab=PV_LABEL[k.s]?'<span class="st s-'+k.s+'">'+PV_LABEL[k.s]+'</span>':'';
  if(k.d){const b=k.b,sz=b.new+b.update+b.same+b.to_a;
   t+='<tr class="fdir s-'+k.s+'"><td><a href="#" data-i="'+i+'">📁 '+pvEsc(k.n)+'</a></td><td>'+(k.s!=='same'?lab:'')+pvCnt(k.c)+'</td><td class="num hide-sm">'+(sz?pvSize(sz):'')+'</td><td class="hide-sm"></td></tr>'}
  else t+='<tr class="ffile s-'+k.s+'"><td>📄 '+pvEsc(k.n)+'</td><td>'+lab+'</td><td class="num hide-sm">'+pvSize(k.size||0)+'</td><td class="hide-sm"><small>'+pvDate(k.m)+'</small></td></tr>'});
 if(!rows.length)t+='<tr><td colspan="4" class="mut" style="padding:14px">'+(only?'Keine Änderungen in diesem Ordner.':'Ordner ist leer.')+'</td></tr>'}
 v.innerHTML='<div class="pvb">'+c+t+'</tbody></table></div></div>';
 v.querySelectorAll('a[data-i]').forEach(a=>a.onclick=e=>{e.preventDefault();pvInto(rows[+a.dataset.i].n)})}
</script>{% endif %}
</div>
<div class="tw-only">
<div class="row" style="margin-top:6px"><div><label>Wenn eine Datei auf beiden Seiten geändert wurde</label>
<select name="bisync_conflict">
<option value="newer" {{ "selected" if (job.bisync_conflict or "newer") == "newer" }}>Die neuere gewinnt, die ältere bleibt umbenannt erhalten (empfohlen)</option>
<option value="none" {{ "selected" if job.bisync_conflict == "none" }}>Beide behalten, beide werden umbenannt</option>
<option value="path1" {{ "selected" if job.bisync_conflict == "path1" }}>Seite A gewinnt, die Fassung von B bleibt umbenannt erhalten</option>
<option value="path2" {{ "selected" if job.bisync_conflict == "path2" }}>Seite B gewinnt, die Fassung von A bleibt umbenannt erhalten</option>
</select>
<div class="hint">Umbenannte Fassungen heißen z. B. <code>bericht.docx.konflikt1</code> und liegen auf beiden Seiten. Es geht also nie etwas verloren.</div></div>
<div style="flex:0 0 240px"><label>Löschschutz</label><div style="display:flex;gap:8px;align-items:center"><input type="number" name="bisync_max_delete" min="1" max="100" value="{{ job.bisync_max_delete or 50 }}" style="width:90px"><span>%</span></div>
<div class="hint">Abbruch ohne Änderung, wenn auf einer Seite mehr als so viel Prozent der Dateien gelöscht würden (z. B. Laufwerk nicht eingehängt).</div></div></div>
<div class="hint" style="border-left:3px solid var(--warn,#d97706);padding-left:10px;margin-top:10px"><b>Erster Lauf:</b> Beim ersten Mal (und nach einer Änderung von Seite A, Seite B, Ausschlüssen oder Prüfsumme) werden beide Seiten zusammengeführt: Was nur auf einer Seite liegt, wird auf die andere kopiert, gelöscht wird dabei nichts. Gibt es eine Datei auf beiden Seiten unterschiedlich, gewinnt die neuere. Erst ab dem zweiten Lauf werden Löschungen übertragen. Tipp: Den ersten Lauf als Testlauf starten.</div>
{% if job_id and job.bisync_need_resync %}<div class="err" style="margin-top:10px">Der letzte Lauf wurde abgebrochen und braucht einen neuen Abgleich. Live-Runden sind bis dahin ausgesetzt. Klicke in der Übersicht oder unten auf „Neu zusammenführen“.</div>{% endif %}
</div>
</div>

<div class="card"><h2>Start</h2>
<label>Wann soll die Aufgabe starten?</label>
<div class="seg" id="trig">
<label><input type="radio" name="trigger" value="time" {{ "checked" if job.trigger == "time" }} onchange="trigShow()"><span>🕒 Zu einer Uhrzeit</span></label>
<label><input type="radio" name="trigger" value="after" {{ "checked" if job.trigger == "after" }} onchange="trigShow()"><span>⛓ Nach einer anderen Aufgabe</span></label>
<label><input type="radio" name="trigger" value="live" {{ "checked" if job.trigger == "live" }} onchange="trigShow()"><span>⚡ Fortlaufend (Live)</span></label>
<label><input type="radio" name="trigger" value="manual" {{ "checked" if job.trigger == "manual" }} onchange="trigShow()"><span>✋ Nur manuell</span></label></div>

<div class="t-live">
<div class="hint tw-only" style="margin-top:0">Jede Runde ist ein Zwei-Wege-Abgleich: Änderungen und Löschungen auf beiden Seiten werden übernommen. Runden ohne Änderung erscheinen nicht im Verlauf. Läufe überlappen nie.</div>
<div class="ow-only">
<label>Bei jeder Runde</label>
<div class="seg" id="lmode" style="flex-wrap:wrap">
<label><input type="radio" name="live_mode" value="mirror" {{ "checked" if job.live_mode != "fast" }} onchange="lmShow()"><span>🪞 Wie Spiegeln: neue, geänderte und gelöschte Dateien übernehmen (empfohlen)</span></label>
<label><input type="radio" name="live_mode" value="fast" {{ "checked" if job.live_mode == "fast" }} onchange="lmShow()"><span>⚡ Schnell: nur neue und geänderte Dateien kopieren, nichts löschen</span></label></div>
</div>
<div class="row" style="align-items:flex-end;margin-top:10px"><div style="flex:0 0 auto"><label>Quelle und Ziel prüfen alle</label>
<div style="display:flex;gap:8px;align-items:center"><input type="number" name="live_interval" min="1" max="1440" value="{{ job.live_interval or 1 }}" style="width:90px"><span>Minuten</span></div></div></div>
<div class="hint lm-mirror">Jede Runde vergleicht Quelle und Ziel wie ein normaler Spiegel-Lauf (<code>rclone sync</code>): Neue und geänderte Dateien werden kopiert, was in der Quelle gelöscht wurde, wird auch im Ziel entfernt. Übertragen wird nur, was sich wirklich geändert hat. Dafür werden bei jeder Runde beide Seiten aufgelistet. Bei sehr vielen Dateien (mehrere 100.000) dauert das länger, dann lieber ein größeres Intervall oder „Schnell“ wählen. Schutz vor Massenlöschung („höchstens N löschen“), Versionierung und Ausschlüsse gelten in jeder Runde.</div>
<div class="lm-fast">
<label class="check" style="margin-top:14px"><input type="checkbox" id="lf_on" {{ "checked" if job.live_full }} onchange="lfSync()"> Zusätzlich regelmäßig voll spiegeln, damit auch Löschungen im Ziel ankommen</label>
<div id="lf_box">
<div class="seg" id="lf_kind" style="margin-bottom:8px"><label><input type="radio" name="lf_kind" value="time" onchange="lfKind()"><span>Zu einer Uhrzeit</span></label><label><input type="radio" name="lf_kind" value="every" onchange="lfKind()"><span>Nach Intervall</span></label><label><input type="radio" name="lf_kind" value="cron" onchange="lfKind()"><span>Cron-Ausdruck</span></label></div>
<div id="lf_every" class="row" style="align-items:flex-end;display:none"><div style="flex:0 0 auto"><label>Voller Abgleich alle</label>
<div style="display:flex;gap:8px;align-items:center"><input type="number" id="lf_n" min="1" max="720" value="6" style="width:90px"><select id="lf_u" style="width:auto"><option value="h">Stunden</option><option value="m">Minuten</option></select></div></div></div>
<div id="lf_simple" class="row" style="align-items:flex-end"><div style="flex:0 0 auto"><label>Voller Abgleich um</label><input type="time" id="lf_time" value="03:00" style="width:130px"></div>
<div><label>Tage</label><div class="days" id="lf_days">{% for n in ["Mo","Di","Mi","Do","Fr","Sa","So"] %}<label><input type="checkbox" value="{{ loop.index % 7 }}" checked><span>{{ n }}</span></label>{% endfor %}</div></div></div>
<div id="lf_cron" style="display:none"><label>Voller Abgleich, Cron-Ausdruck (Zeitzone {{ tz }})</label><input type="text" id="lf_expr" value="{{ job.live_full }}" placeholder="0 3 * * *"></div>
</div>
<input type="hidden" name="live_full" id="live_full" value="{{ job.live_full }}">
<div class="hint">Die schnellen Läufe kopieren nur, was sich seit dem letzten erfolgreichen Lauf geändert hat (<code>rclone copy --max-age</code>), und löschen nichts.
Läufe überlappen nie: Ist der vorige noch nicht fertig, wird die Runde ausgelassen. Läufe ohne Änderung erscheinen nicht im Verlauf und lösen keine Benachrichtigung aus, ein Fehler wird einmal gemeldet.
Der erste Lauf und der nach einer Änderung von Quelle, Ziel oder Ausschlüssen ist ein voller Abgleich. Bandbreitenregeln gelten auch hier.
Dateien, die mit altem Änderungsdatum in die Quelle kommen (z. B. verschoben oder aus einem Archiv entpackt), kommen erst mit dem vollen Abgleich an.{% if followers %} Folgeaufgaben starten nur nach dem vollen Abgleich.{% endif %}</div>
</div>
<div class="hint lm-mirror">Läufe überlappen nie: Ist der vorige noch nicht fertig, wird die Runde ausgelassen. Runden ohne Änderung erscheinen nicht im Verlauf und lösen keine Benachrichtigung aus, ein Fehler wird einmal gemeldet. Bandbreitenregeln gelten auch hier. Ist „nur Testlauf“ an, fallen die Live-Runden aus.{% if followers %} Folgeaufgaben starten nach jeder Runde, die etwas geändert hat.{% endif %}</div>
</div>

<div class="t-time">
<div id="simple">
<div class="row" style="align-items:flex-end"><div style="flex:0 0 auto"><label>Uhrzeit</label><input type="time" id="s_time" value="03:00" style="width:130px"></div>
<div><label>Tage</label><div class="days" id="s_days">{% for n in ["Mo","Di","Mi","Do","Fr","Sa","So"] %}<label><input type="checkbox" value="{{ loop.index % 7 }}" checked><span>{{ n }}</span></label>{% endfor %}</div></div></div>
<div class="hint"><a href="#" onclick="cronMode(true);return false">Erweitert: mehrmals am Tag, alle X Minuten (Cron-Ausdruck)</a></div>
</div>
<div id="cron" style="display:none">
<div class="row"><div style="flex:2"><label>Cron-Ausdruck (Zeitzone {{ tz }})</label><input type="text" id="schedule" name="schedule" value="{{ job.schedule }}" placeholder="30 1 * * *"></div>
<div><label>Vorlage</label><select onchange="if(this.value){document.getElementById('schedule').value=this.value;cronPrev()}">
<option value="">Vorlage wählen…</option>
<option value="*/15 * * * *">alle 15 Minuten</option><option value="0 * * * *">stündlich</option>
<option value="0 */6 * * *">alle 6 Stunden</option><option value="0 3 * * *">täglich 03:00</option>
<option value="0 22 * * 1-5">werktags 22:00</option><option value="0 4 * * 0">sonntags 04:00</option>
<option value="0 2 1 * *">monatlich am 1. um 02:00</option></select></div></div>
<div class="hint">Format: Minute Stunde Tag Monat Wochentag. Beispiel <code>30 1 * * *</code> = täglich 01:30. <a href="#" onclick="cronMode(false);return false">Einfache Auswahl</a></div>
</div>
<div class="hint" id="cronprev"></div>
</div>

<div class="t-after">
<div class="row"><div style="flex:2"><label>Starten nach</label><select name="after_job" id="after_job">
<option value="">– Aufgabe wählen –</option>
{% for o in others %}<option value="{{ o.id }}" {{ "selected" if job.after_job == o.id }} {{ "disabled" if o.loop }}>{{ o.name }}{% if o.loop %} (würde eine Schleife bilden){% endif %}</option>{% endfor %}</select></div>
<div><label>Bedingung</label><select name="after_when">
<option value="ok" {{ "selected" if job.after_when != "always" }}>nur wenn sie erfolgreich war</option>
<option value="always" {{ "selected" if job.after_when == "always" }}>immer, auch nach einem Fehler</option></select></div></div>
<div class="hint">Startet, sobald die gewählte Aufgabe fertig ist, egal ob sie nach Zeitplan, von Hand oder selbst als Folgeaufgabe lief. Nach einem Testlauf oder einem Stopp startet nichts.{% if not others %} <span class="fehler">Es gibt noch keine andere Aufgabe.</span>{% endif %}</div>
</div>
<div class="t-manual hint">Startet nur über „Start“ in der Übersicht{% if followers %} oder als Kette{% endif %}.</div>
{% if followers %}<div class="msg info" style="margin-top:12px">Danach starten: <b>{{ followers|join(", ") }}</b></div>{% endif %}
<label class="check t-on"><input type="checkbox" name="enabled" {{ "checked" if job.enabled }}> Automatischen Start aktivieren</label>
<div class="section" style="margin-top:14px">
<label class="check" style="font-weight:600"><input type="checkbox" name="paused" id="paused" {{ "checked" if job.paused }} onchange="document.getElementById('pbox').style.display=this.checked?'':'none'"> Aufgabe pausieren</label>
<div id="pbox" style="{{ '' if job.paused else 'display:none' }}">
<div class="row"><div><label>Pausiert bis (leer = bis ich fortsetze)</label><input type="datetime-local" name="paused_until" value="{{ job.paused_until }}"></div><div></div></div>
<div class="hint">Während der Pause startet die Aufgabe weder nach Zeitplan noch live noch als Teil einer Kette. Von Hand starten geht weiter. Danach läuft sie automatisch wieder normal.{% if job.paused_by %} Pausiert von {{ job.paused_by }}.{% endif %}</div></div>
<label style="margin-top:10px">Wenn sie in einer Kette an der Reihe ist und pausiert ist</label>
<select name="pause_chain"><option value="skip" {{ "selected" if job.pause_chain != "stop" }}>überspringen, nachfolgende Aufgaben laufen weiter</option>
<option value="stop" {{ "selected" if job.pause_chain == "stop" }}>Kette hier anhalten, nachfolgende Aufgaben laufen nicht</option></select>
</div>
</div>
<script>
const LF=document.getElementById('live_full');
function isTW(){return (document.querySelector('[name=direction]:checked')||document.querySelector('[name=direction][type=hidden]')||{}).value==='bisync'}
function lmShow(){const tw=isTW(),f=!tw&&(document.querySelector('[name=live_mode]:checked')||{}).value==='fast';
  document.querySelectorAll('.lm-fast').forEach(e=>e.style.display=f?'':'none');document.querySelectorAll('.lm-mirror').forEach(e=>e.style.display=f||tw?'none':'')}
function dirShow(){const tw=isTW();if(window.destPreview&&document.getElementById('destprev'))destPreview();document.querySelectorAll('.tw-only').forEach(e=>e.style.display=tw?'':'none');document.querySelectorAll('.ow-only').forEach(e=>e.style.display=tw?'none':'');
  document.getElementById('h_sd').textContent=tw?'Seite A und Seite B':'Quelle und Ziel';
  document.getElementById('lbl_src').textContent=tw?'Seite A':'Quelle';document.getElementById('lbl_dst').textContent=tw?'Seite B':'Ziel (wird an die Quelle angeglichen)';
  if(typeof lmShow==='function')lmShow()}
function lfKind(){const k=(document.querySelector('[name=lf_kind]:checked')||{}).value||'time';
  document.getElementById('lf_simple').style.display=k==='time'?'':'none';document.getElementById('lf_every').style.display=k==='every'?'':'none';
  document.getElementById('lf_cron').style.display=k==='cron'?'':'none';lfSync()}
function lfSync(){const on=document.getElementById('lf_on').checked;document.getElementById('lf_box').style.display=on?'':'none';
  if(!on){LF.value='';return}
  const k=(document.querySelector('[name=lf_kind]:checked')||{}).value||'time';
  if(k==='every'){LF.value='@every '+Math.max(1,parseInt(document.getElementById('lf_n').value)||1)+document.getElementById('lf_u').value;return}
  if(k==='cron'){LF.value=document.getElementById('lf_expr').value.trim();return}
  const [h,m]=(document.getElementById('lf_time').value||'03:00').split(':');const d=[...document.querySelectorAll('#lf_days input:checked')].map(i=>+i.value).sort();
  let dw='*';if(d.length&&d.length<7){const g=[];d.forEach(x=>{const l=g[g.length-1];if(l&&x===l[1]+1)l[1]=x;else g.push([x,x])});dw=g.map(([a,b])=>a===b?a:(b===a+1?a+','+b:a+'-'+b)).join(',')}
  LF.value=(+m)+' '+(+h)+' * * '+dw}
(function(){const v=LF.value.trim()||'0 3 * * *',m=v.match(/^(\d{1,2}) (\d{1,2}) \* \* (\*|[0-6](?:[-,][0-6])*)$/),ev=v.match(/^@every\s+(\d+)\s*([mh])$/);
  const kind=k=>{document.querySelector('[name=lf_kind][value='+k+']').checked=true};
  if(ev){document.getElementById('lf_n').value=ev[1];document.getElementById('lf_u').value=ev[2];kind('every')}
  else if(m){kind('time');document.getElementById('lf_time').value=String(m[2]).padStart(2,'0')+':'+String(m[1]).padStart(2,'0');
    const ds=m[3]==='*'?[0,1,2,3,4,5,6]:m[3].split(',').flatMap(p=>{const [a,b]=p.split('-').map(Number);return b===undefined?[a]:Array.from({length:b-a+1},(_,i)=>a+i)});
    document.querySelectorAll('#lf_days input').forEach(i=>i.checked=ds.includes(+i.value))}
  else kind('cron');
  ['lf_time','lf_expr','lf_n'].forEach(id=>document.getElementById(id).addEventListener('input',lfSync));
  document.getElementById('lf_u').addEventListener('change',lfSync);dirShow();lfKind();document.addEventListener('DOMContentLoaded',dirShow);
  document.querySelectorAll('#lf_days input').forEach(i=>i.addEventListener('change',lfSync));lfSync()})();
const SD=document.getElementById('schedule');
function trigShow(){const t=document.querySelector('[name=trigger]:checked').value;
  document.querySelector('.t-time').style.display=t==='time'?'':'none';document.querySelector('.t-after').style.display=t==='after'?'':'none';
  document.querySelector('.t-live').style.display=t==='live'?'':'none';
  document.querySelector('.t-manual').style.display=t==='manual'?'':'none';document.querySelector('.t-on').style.display=t==='manual'?'none':''}
function simpleToCron(){const [h,m]=(document.getElementById('s_time').value||'03:00').split(':');
  const d=[...document.querySelectorAll('#s_days input:checked')].map(i=>+i.value).sort();
  let dw='*';if(d.length&&d.length<7){const g=[];d.forEach(x=>{const l=g[g.length-1];if(l&&x===l[1]+1)l[1]=x;else g.push([x,x])});
    dw=g.map(([a,b])=>a===b?a:(b===a+1?a+','+b:a+'-'+b)).join(',')}
  SD.value=(+m)+' '+(+h)+' * * '+dw;cronPrev()}
function cronMode(adv){document.getElementById('simple').style.display=adv?'none':'';document.getElementById('cron').style.display=adv?'':'none';if(!adv)simpleToCron();cronPrev()}
function cronPrev(){const v=SD.value.trim(),m=v.match(/^(\d{1,2}) (\d{1,2}) \* \* (\*|[0-7](?:[-,][0-7])*)$/),el=document.getElementById('cronprev');
  if(!m){el.textContent=v?'':'';return}
  const N=['So','Mo','Di','Mi','Do','Fr','Sa','So'],t=String(m[2]).padStart(2,'0')+':'+String(m[1]).padStart(2,'0');
  let d=m[3]==='*'?'täglich':m[3]==='1-5'?'Mo–Fr':m[3].split(',').map(p=>p.split('-').map(x=>N[+x]).join('–')).join(', ');
  el.textContent='Startet {0} um {1} Uhr ({2}).'.replace('{0}',d).replace('{1}',t).replace('{2}',TZN)}
const TZN='{{ tz }}';
(function(){const v=SD.value.trim(),m=v.match(/^(\d{1,2}) (\d{1,2}) \* \* (\*|[0-6](?:[-,][0-6])*)$/);
  if(m||!v){if(m){document.getElementById('s_time').value=String(m[2]).padStart(2,'0')+':'+String(m[1]).padStart(2,'0');
    const ds=m[3]==='*'?[0,1,2,3,4,5,6]:m[3].split(',').flatMap(p=>{const [a,b]=p.split('-').map(Number);return b===undefined?[a]:Array.from({length:b-a+1},(_,i)=>a+i)});
    document.querySelectorAll('#s_days input').forEach(i=>i.checked=ds.includes(+i.value))} cronMode(false)} else cronMode(true);
  document.getElementById('s_time').addEventListener('input',simpleToCron);document.querySelectorAll('#s_days input').forEach(i=>i.addEventListener('change',simpleToCron));
  SD.addEventListener('input',cronPrev);trigShow()})();
</script>

<div class="card"><h2>Ausschlüsse</h2>
<textarea name="excludes" id="excludes" rows="5" placeholder="/Temp/&#10;/Projekte/alt/&#10;*.tmp&#10;**/node_modules/**">{{ job.excludes }}</textarea>
<button type="button" class="btn sm" style="margin-top:8px{{ ';display:none' if not can('remotes.browse') }}" onclick="openFB('ex')">{{ ICON.plus }} Ordner oder Dateien aus der Quelle ausschließen</button>
<div class="hint">Ein Eintrag pro Zeile, relativ zur Quelle. <code>/Temp/</code> = Ordner Temp direkt in der Quelle,
<code>Temp/</code> = jeder Ordner namens Temp, <code>/Projekte/alt/bericht.docx</code> = eine Datei, <code>*.tmp</code> = alle .tmp-Dateien.</div>
<div class="ow-only"><label class="check"><input type="checkbox" name="no_delete" {{ "checked" if job.no_delete }}> Im Ziel nichts löschen: nur Neues und Geändertes kopieren (<code>rclone copy</code> statt <code>sync</code>). Was in der Quelle gelöscht wurde, bleibt im Ziel liegen.</label></div>
<div class="ow-only"><label class="check"><input type="checkbox" name="delete_excluded" {{ "checked" if job.delete_excluded }}> Ausgeschlossenes auch im Ziel löschen (sonst bleibt es dort unangetastet liegen)</label>
<div class="hint">Bei einer Auswahl (☑) gilt das nicht: Dann bleibt im Ziel alles außerhalb der Auswahl immer unberührt.</div></div>
<div class="hint tw-only">Beim Zwei-Wege-Sync gelten die Ausschlüsse für beide Seiten: Ausgeschlossenes wird auf keiner Seite angefasst.</div>
</div>

<div class="card"><h2>Benachrichtigungen</h2><fieldset {{ "disabled" if not can("jobs.notify") }}>{% if not can("jobs.notify") %}<div class="hint" style="margin-bottom:8px">Deine Rolle darf die Benachrichtigungen dieser Aufgabe nicht ändern.</div>{% endif %}
<div class="row"><div><label>Für diese Aufgabe</label>
<select name="notify_mode" id="nmode" onchange="nshow()">
<option value="global" {{ "selected" if job.notify_mode == "global" }}>Standard verwenden{% if glob.summary %} ({{ glob.summary }}){% endif %}</option>
<option value="custom" {{ "selected" if job.notify_mode == "custom" }}>Eigene Benachrichtigung für diese Aufgabe</option>
<option value="off" {{ "selected" if job.notify_mode == "off" }}>Keine Benachrichtigung</option></select></div>
<div class="ncustom"><label>Wann</label><select name="notify_when">
<option value="fail" {{ "selected" if job.notify_when != "always" }}>nur bei Fehler</option>
<option value="always" {{ "selected" if job.notify_when == "always" }}>immer (Erfolg und Fehler)</option></select></div></div>
<div class="hint nglobal">Den Standard legst du unter <a href="/settings">Benachrichtigungen</a> fest.</div>

<div class="ncustom">
<div class="section"><label class="check" style="font-weight:600"><input type="checkbox" name="notify_webhook" {{ "checked" if job.notify_webhook }}> Webhook</label>
<input type="text" name="notify_webhook_url" value="{{ job.notify_webhook_url }}" placeholder="{{ glob.webhook_url or 'https://ntfy.sh/mein-thema, Discord-, Slack-, Home-Assistant-, n8n-Webhook' }}">
<div class="hint">{% if glob.webhook %}Leer = Standard-URL verwenden.{% else %}URL eintragen, an die bei jedem Ereignis JSON gesendet wird.{% endif %}</div></div>

<div class="section"><label class="check" style="font-weight:600"><input type="checkbox" name="notify_smtp" {{ "checked" if job.notify_smtp }}> E-Mail</label>
<input type="text" name="notify_smtp_to" value="{{ job.notify_smtp_to }}" placeholder="{{ glob.smtp_to or 'empfaenger@example.de, zweiter@example.de' }}">
<div class="hint">{% if glob.smtp %}Empfänger für diese Aufgabe, leer = Standard-Empfänger. Versand über den SMTP-Server aus den <a href="/settings">Einstellungen</a>.
{% else %}<span class="fehler">Noch kein SMTP-Server eingerichtet.</span> Den Mailserver trägst du einmal unter <a href="/settings">Benachrichtigungen</a> ein.{% endif %}</div></div>

<div class="section"><label class="check" style="font-weight:600"><input type="checkbox" name="notify_telegram" {{ "checked" if job.notify_telegram }}> Telegram</label>
<div class="row"><div><input type="text" name="notify_telegram_chat_id" value="{{ job.notify_telegram_chat_id }}" placeholder="Chat-ID{{ ' (Standard: ' ~ glob.telegram_chat_id ~ ')' if glob.telegram_chat_id }}"></div>
<div><input type="password" name="notify_telegram_token" autocomplete="new-password" placeholder="{{ '(eigener Bot-Token gespeichert)' if has_token else ('Bot-Token (leer = Standard-Bot)' if glob.telegram else 'Bot-Token von @BotFather') }}"></div></div>
{% if has_token %}<label class="check"><input type="checkbox" name="notify_telegram_token_clear"> eigenen Bot-Token entfernen</label>{% endif %}
<div class="hint">Chat-ID oder Bot nur für diese Aufgabe, leer = Standard aus den <a href="/settings">Einstellungen</a>.</div></div>

<div class="section"><label class="check" style="font-weight:600"><input type="checkbox" name="notify_apprise" {{ "checked" if job.notify_apprise }}> Apprise</label>
<textarea name="notify_apprise_urls" rows="2" autocomplete="off" spellcheck="false" placeholder="{{ ('Eigene gespeichert: ' ~ job.apprise_saved ~ ' (leer lassen = unverändert)') if job.apprise_saved else ('Eigene Apprise-URLs, eine pro Zeile (leer = Standard-URLs)' if glob.apprise_ready else 'ntfy://ntfy.sh/mein-thema, discord://…') }}"></textarea>
{% if job.apprise_saved %}<label class="check"><input type="checkbox" name="notify_apprise_urls_clear"> eigene URLs entfernen</label>{% endif %}
<div class="row"><div><input type="text" name="notify_apprise_tag" value="{{ job.notify_apprise_tag }}" placeholder="Tag{{ ' (Standard: ' ~ glob.apprise_tag ~ ')' if glob.apprise_tag else ' (optional)' }}"></div><div></div></div>
<div class="hint">Versand wie unter <a href="/settings">Benachrichtigungen</a> eingestellt (direkt oder über den Apprise-API-Server). Eigene URLs oder Tag gelten nur für diese Aufgabe.</div></div>
</div>
<div class="ntexts" style="margin-top:14px">
<label class="check"><input type="checkbox" name="msg_tpl_on" id="mtpl" {{ "checked" if job.msg_tpl_on }} onchange="document.getElementById('jtplbox').style.display=this.checked?'':'none'"> Eigene Texte für diese Aufgabe</label>
<div id="jtplbox" style="{{ '' if job.msg_tpl_on else 'display:none' }}">{% with items=jtpl, prefix="jtpl_" %}{% include "tpl_editor.html" %}{% endwith %}
<div class="hint">Ohne Änderung gilt der Text aus <a href="/settings">Benachrichtigungen</a>. Der Test-Knopf schickt den Text „Lauf erfolgreich“ mit Beispielzahlen.</div></div></div>
<p style="margin:16px 0 0"><button type="button" class="btn sm" onclick="ntest()">{{ ICON.bell }} Testnachricht senden</button> <span id="nres" class="hint"></span></p></fieldset>
</div>

<div class="card"><h2>Bandbreite</h2>
<label>Für diese Aufgabe</label>
<select name="bw_mode" id="bwmode" onchange="bwshow()">
<option value="global" {{ "selected" if (job.bw_mode or "global") == "global" }}>Standard verwenden ({{ glob.bw }})</option>
<option value="custom" {{ "selected" if job.bw_mode == "custom" }}>Eigene Grenzen für diese Aufgabe</option>
<option value="off" {{ "selected" if job.bw_mode == "off" }}>Immer unbegrenzt</option></select>
<div class="hint bwglobal">Den Standard legst du unter {% if can("system.settings") %}<a href="/settings/general">Einstellungen → Allgemein</a>{% else %}Einstellungen → Allgemein{% endif %} fest.</div>
<div id="bwcustom" style="margin-top:12px">{% include "bw_editor.html" %}</div>
<script>function bwshow(){const c=document.getElementById('bwmode').value;document.getElementById('bwcustom').style.display=c==='custom'?'':'none';document.querySelector('.bwglobal').style.display=c==='global'?'':'none'}bwshow()</script>
</div>

{% with vis=job.get("visible_to"), vis_what="job" %}{% include "vis_picker.html" %}{% endwith %}

{% set W = job.window or {} %}<div class="card"><h2>Zeitfenster</h2>
<label class="check"><input type="checkbox" name="window_on" id="win_on" {{ "checked" if job.window }} onchange="winShow()"> Nur in einem Zeitfenster laufen lassen</label>
<div id="winbox" style="{{ '' if job.window else 'display:none' }}">
<div class="row" style="margin-top:6px">
<div style="flex:0 0 150px"><label for="window_start">Von</label><input type="time" name="window_start" id="window_start" value="{{ W.start or '22:00' }}"></div>
<div style="flex:0 0 150px"><label for="window_end">Bis</label><input type="time" name="window_end" id="window_end" value="{{ W.end or '06:00' }}"></div>
<div style="flex:1 1 280px"><label>An diesen Tagen (Beginn des Fensters)</label><div class="chips" style="margin:4px 0 0">{% for d in range(7) %}<label class="check" style="margin:0 10px 0 0"><input type="checkbox" name="window_day_{{ d }}" {{ "checked" if (not W.days) or d in W.days }}> {{ ["Mo","Di","Mi","Do","Fr","Sa","So"][d] }}</label>{% endfor %}</div></div></div>
<div style="margin-top:10px"><label for="window_mode">Wenn das Fenster endet und die Aufgabe noch läuft</label><select name="window_mode" id="window_mode" style="max-width:520px">
<option value="finish" {{ "selected" if W.mode == "finish" or not W.mode }}>Bis zum Ende durchlaufen lassen</option>
<option value="resume" {{ "selected" if W.mode == "resume" }}>Anhalten und im nächsten Fenster weitermachen</option>
<option value="stop" {{ "selected" if W.mode == "stop" }}>Anhalten, erst der nächste reguläre Start läuft wieder</option></select></div>
<div class="hint">Zeitplan, Live und Ketten starten nur innerhalb des Fensters. Fällt ein Start in die Zeit außerhalb, startet die Aufgabe, sobald das Fenster aufgeht (Live-Runden entfallen einfach). Geht das Ende über Mitternacht (z. B. 22:00 bis 06:00), zählt der Wochentag des Beginns. Beim Weitermachen wird schon Kopiertes übersprungen. Von Hand gestartete Läufe außerhalb des Fensters laufen immer durch.</div>
</div></div>
<script>function winShow(){document.getElementById('winbox').style.display=document.getElementById('win_on').checked?'':'none'}</script>

<div class="card"><h2>Optionen</h2>
<label class="check"><input type="checkbox" name="versioning" id="vers" {{ "checked" if job.versioning }} onchange="document.getElementById('versbox').style.display=this.checked?'':'none'"> Papierkorb/Versionierung: gelöschte und überschriebene Dateien nach <code>&lt;ziel&gt;.versions/&lt;datum&gt;</code> verschieben statt löschen{% if job_id and job.versioning and can("jobs.restore") %} · <a href="/job/{{ job_id }}/versions">Dateien suchen und wiederherstellen</a>{% endif %}</label>
<div id="versbox" class="row" style="margin:0 0 8px 26px;{{ '' if job.versioning else 'display:none' }}">
<div style="flex:0 0 220px"><label>Versionen behalten</label><input type="text" name="versions_keep" inputmode="numeric" value="{{ job.versions_keep or '' }}" placeholder="alle"><div class="hint">Anzahl Stände, z. B. 10. Leer = alle.</div></div>
<div style="flex:0 0 220px"><label>Höchstens so alt (Tage)</label><input type="text" name="versions_days" inputmode="numeric" value="{{ job.versions_days or '' }}" placeholder="unbegrenzt"><div class="hint">z. B. 30. Leer = unbegrenzt.</div></div>
<div><div class="hint" style="margin-top:28px">Jeder Lauf, der etwas überschreibt oder löscht, legt einen Stand (Ordner mit Datum) an. Nach jedem erfolgreichen Lauf werden ältere Stände entfernt.</div></div></div>
<div class="row" style="margin:4px 0 10px">
<div style="flex:1 1 300px"><label for="compare">Änderung erkennen an</label><select name="compare" id="compare" onchange="cmpShow()">
<option value="standard" {{ "selected" if job.compare == "standard" }}>Größe und Änderungszeit (Standard)</option>
<option value="size" {{ "selected" if job.compare == "size" }}>Nur Größe (am schnellsten)</option>
<option value="checksum" {{ "selected" if job.compare == "checksum" }}>Prüfsumme (am sichersten, langsam)</option>
<option value="tolerant" {{ "selected" if job.compare == "tolerant" }}>Größe und Änderungszeit mit Toleranz</option></select>
<div class="hint" id="cmphint"></div></div>
<div style="flex:0 0 200px" id="cmpwin"><label for="compare_window">Toleranz (Sekunden)</label><input type="text" inputmode="numeric" name="compare_window" id="compare_window" value="{{ job.compare_window or '2' }}">
<div class="hint">2 = FAT/exFAT, 3600 = Zeitumstellung</div></div>
<div style="flex:1 1 260px"><label for="speed">Tempo</label><select name="speed" id="speed" onchange="cmpShow()">
<option value="gentle" {{ "selected" if job.speed == "gentle" }}>Schonend (2 parallel)</option>
<option value="normal" {{ "selected" if job.speed == "normal" }}>Normal (4 parallel)</option>
<option value="fast" {{ "selected" if job.speed == "fast" }}>Schnell (8 parallel)</option>
<option value="max" {{ "selected" if job.speed == "max" }}>Sehr schnell (16 parallel)</option></select>
<div class="hint" id="spdhint"></div></div></div>
<script>function cmpShow(){const c=document.getElementById('compare').value,sp=document.getElementById('speed').value;
document.getElementById('cmpwin').style.display=c==='tolerant'?'':'none';
document.getElementById('cmphint').textContent={standard:'Eine Datei wird übertragen, wenn Größe oder Änderungszeit abweichen. Schnell und für die meisten Fälle richtig.',
 size:'Nur die Größe zählt. Am schnellsten, übersieht aber Änderungen, bei denen die Größe gleich bleibt.',
 checksum:'Vergleicht den Inhalt per Prüfsumme. Am sichersten, aber jede Datei wird gelesen. Ohne gemeinsame Prüfsumme beider Seiten wie Standard.',
 tolerant:'Änderungszeiten dürfen um die Toleranz abweichen. Hilft bei SMB, FAT und USB-Platten, die Zeiten ungenau speichern.'}[c];
document.getElementById('spdhint').textContent={gentle:'Schont Server, Platten und Leitung.',normal:'rclone-Standard: 4 Übertragungen und 8 Prüfungen gleichzeitig.',
 fast:'8 Übertragungen, 16 Prüfungen, Ordner in einem Rutsch auflisten. Gut bei vielen kleinen Dateien.',
 max:'16 Übertragungen, 32 Prüfungen. Braucht mehr Speicher und Leistung auf beiden Seiten.'}[sp]}cmpShow()</script>
<label class="check"><input type="checkbox" name="dry_run" {{ "checked" if job.dry_run }}> Immer nur Testlauf (nichts wird verändert)</label>
<div class="row"><div class="ow-only"><label>Max. Löschungen pro Lauf</label><input type="text" name="max_delete" value="{{ job.max_delete }}">
<div class="hint">Schutz, falls die Quelle plötzlich leer ist. Leer = kein Limit.</div></div>
<div><label>Zusätzliche rclone-Optionen</label><input type="text" name="extra_flags" value="{{ job.extra_flags }}" {{ "disabled" if not can("jobs.advanced") }} placeholder='--transfers 8'>
<div class="hint">z. B. parallele Übertragungen. Ein eigenes <code>--bwlimit</code> hier ersetzt die Einstellung „Bandbreite“.</div></div></div>
</div>

<div class="card" id="protect"><h2>Prüfen und schützen</h2>
<div class="row"><div style="flex:1 1 300px"><label for="verify">Prüflauf nach dem Sync</label><select name="verify" id="verify">
<option value="off" {{ "selected" if (job.verify or "off") == "off" }}>aus</option>
<option value="always" {{ "selected" if job.verify == "always" }}>nach jedem Lauf</option>
<option value="daily" {{ "selected" if job.verify == "daily" }}>höchstens einmal am Tag</option>
<option value="weekly" {{ "selected" if job.verify == "weekly" }}>höchstens einmal in der Woche</option></select></div>
<div style="flex:1 1 300px"><label for="verify_method">Vergleich</label><select name="verify_method" id="verify_method">
<option value="auto" {{ "selected" if (job.verify_method or "auto") == "auto" }}>Prüfsumme, wenn beide Seiten eine haben, sonst Größe</option>
<option value="size" {{ "selected" if job.verify_method == "size" }}>Nur Größe (schnell)</option>
<option value="download" {{ "selected" if job.verify_method == "download" }}>Inhalt Byte für Byte (liest alles, sicher bei jedem Speicher)</option></select></div></div>
<div class="hint">Vergleicht nach einem erfolgreichen Lauf Quelle und Ziel Datei für Datei (<code>rclone check</code>). Im Verlauf steht dann schwarz auf weiß „1:1 gleich“ oder welche Dateien abweichen; Abweichungen machen den Lauf zum Fehler und lösen die Benachrichtigung aus. „Jetzt prüfen“ im Log startet die Prüfung jederzeit von Hand.</div>
<div class="row ow-only" style="margin-top:6px"><div style="flex:0 0 220px"><label for="delete_guard">Löschwarnung ab (% der Dateien)</label><input type="text" inputmode="numeric" name="delete_guard" id="delete_guard" value="{{ job.delete_guard or '' }}" placeholder="aus, z. B. 20"></div>
<div style="flex:0 0 220px"><label for="delete_guard_min">und mindestens (Dateien)</label><input type="text" inputmode="numeric" name="delete_guard_min" id="delete_guard_min" value="{{ job.delete_guard_min or '10' }}"></div>
<div><div class="hint" style="margin-top:28px">Vor jedem echten Lauf spielt MirrorSync den Abgleich als Test durch. Würden so viele Dateien im Ziel gelöscht, hält der Lauf an, nichts wird verändert, und du bekommst eine Nachricht. Erst nach deiner Freigabe läuft er. Schützt vor Ransomware und einer versehentlich leeren Quelle. Kostet pro Lauf einen zusätzlichen Testlauf.</div></div></div>
<div class="row" style="margin-top:6px"><div style="flex:0 0 280px"><label for="space_check">Speicher am Ziel prüfen</label><select name="space_check" id="space_check">
<option value="off" {{ "selected" if (job.space_check or "off") == "off" }}>aus</option>
<option value="warn" {{ "selected" if job.space_check == "warn" }}>warnen, Lauf startet trotzdem</option>
<option value="stop" {{ "selected" if job.space_check == "stop" }}>Lauf nicht starten</option></select></div>
<div style="flex:0 0 220px"><label for="space_min_gb">Mindestens frei bleiben (GB)</label><input type="text" inputmode="decimal" name="space_min_gb" id="space_min_gb" value="{{ job.space_min_gb or '' }}" placeholder="nur benötigter Platz"></div>
<div><div class="hint" style="margin-top:28px">Vor dem Lauf wird ermittelt, wie viel kopiert wird, und mit dem freien Platz am Ziel verglichen, damit der Sync nicht mittendrin abbricht. Geht nur, wenn der Speicherort den freien Platz meldet (lokal, SMB, SFTP mit df, viele Clouds).</div></div></div>
<div class="row" style="margin-top:6px"><div style="flex:0 0 280px"><label for="retry">Bei Fehler neu versuchen nach (Minuten)</label><input type="text" name="retry" id="retry" value="{{ job.retry or '' }}" placeholder="aus, z. B. 5, 15, 60"></div>
<div style="flex:0 0 280px"><label for="retry_on">Neu versuchen bei</label><select name="retry_on" id="retry_on">
<option value="network" {{ "selected" if job.retry_on != "any" }}>Netzwerkproblemen</option>
<option value="any" {{ "selected" if job.retry_on == "any" }}>jedem Fehler</option></select></div>
<div><div class="hint" style="margin-top:28px">Scheitert ein Lauf, startet er nach den angegebenen Minuten erneut. Gemeldet wird erst, wenn auch der letzte Versuch scheitert. Gilt nicht für Testläufe und Live-Runden.</div></div></div>
<label class="check" style="margin-top:12px"><input type="checkbox" name="nosync" {{ "checked" if job.nosync }}> Ordner mit einer Datei <code>.nosync</code> überspringen</label>
<div class="hint" style="margin:-4px 0 0 26px">Liegt in einem Ordner der Quelle eine Datei namens <code>.nosync</code>, wird er samt Unterordnern ausgelassen; was davon schon im Ziel liegt, bleibt dort unberührt. Die Quelle wird dafür bei jedem vollen Lauf einmal nach <code>.nosync</code> durchsucht.</div>
<div class="row" style="margin-top:6px"><div style="flex:0 0 280px"><label for="health_max_age">Überfällig nach (Stunden)</label><input type="text" inputmode="decimal" name="health_max_age" id="health_max_age" value="{{ job.health_max_age or '' }}" placeholder="automatisch"></div>
<div><div class="hint" style="margin-top:28px">Für den Health-Status (<code>/health/jobs</code>, Uptime Kuma, Home Assistant): Ist der letzte Lauf älter, gilt die Aufgabe als überfällig. Leer = aus dem Zeitplan berechnet (doppelter Abstand plus eine Stunde).</div></div></div>
</div>

{% set enc_ok = can("jobs.encrypt") %}<div class="card" id="encrypt"><h2>🔒 Ziel verschlüsseln</h2>
{% if not enc_ok %}<div class="msg info">Zum Ändern fehlt dir das Recht „Verschlüsselung des Ziels einrichten oder ausschalten“.</div>{% endif %}
<fieldset {{ "disabled" if not enc_ok }}>
<label class="check"><input type="checkbox" name="encrypt" id="enc" {{ "checked" if job.encrypt }} onchange="encShow()"> Daten im Ziel verschlüsseln, sodass dort niemand sie lesen kann</label>
<div class="hint" style="margin:-4px 0 0 26px">MirrorSync legt dafür einen verschlüsselten Speicherort (rclone crypt) über das Ziel. Darin liegen die Dateien im Ordner <code>data</code>, der Papierkorb in <code>data.versions</code>; im Ziel selbst sieht man nur verschlüsselte Namen und Inhalte. Lesen lassen sie sich nur mit dem Passwort, z. B. über die Wiederherstellung hier oder mit rclone. Geht nicht zusammen mit dem Zwei-Wege-Sync.</div>
<div id="encbox" style="margin-top:10px{{ ';display:none' if not job.encrypt }}">
{% if enc_locked %}<div class="msg info">Die Verschlüsselung ist eingerichtet (Speicherort <code>{{ enc_remote }}</code>). Passwort und Art der Dateinamen stehen fest und lassen sich nicht mehr ändern, sonst wären die vorhandenen Daten nicht mehr lesbar.</div>
<div class="row"><div style="flex:1 1 260px"><label for="encpw">Passwort prüfen (optional)</label><input type="password" name="encrypt_password" id="encpw" autocomplete="off" placeholder="leer lassen"></div>
<div><div class="hint" style="margin-top:28px">Gibst du hier ein Passwort ein, prüft MirrorSync beim Speichern, ob es das richtige ist.</div></div></div>
{% else %}<div class="msg err" style="margin-bottom:10px"><b>Wichtig:</b> Ohne das Passwort sind die Daten im Ziel für immer verloren. Es gibt keine Hintertür und keine Wiederherstellung. Bewahre das Passwort an einem sicheren Ort außerhalb dieses Servers auf, z. B. in einem Passwort-Manager.</div>
<div class="row"><div style="flex:1 1 220px"><label for="encpw">Passwort (mind. {{ enc_min }} Zeichen)</label><input type="password" name="encrypt_password" id="encpw" autocomplete="new-password" minlength="{{ enc_min }}"></div>
<div style="flex:1 1 220px"><label for="encpw2">Passwort wiederholen</label><input type="password" name="encrypt_password_confirm" id="encpw2" autocomplete="new-password"></div></div>
<div class="row"><div style="flex:1 1 220px"><label for="encnames">Dateinamen</label><select name="encrypt_names" id="encnames">
<option value="standard" {{ "selected" if (job.encrypt_names or "standard") == "standard" }}>verschlüsseln (empfohlen)</option>
<option value="obfuscate" {{ "selected" if job.encrypt_names == "obfuscate" }}>nur verschleiern (kürzer)</option>
<option value="off" {{ "selected" if job.encrypt_names == "off" }}>lesbar lassen</option></select></div>
<div style="flex:1 1 220px"><label for="encsalt">Zweites Passwort (Salt, optional)</label><input type="password" name="encrypt_password2" id="encsalt" autocomplete="new-password" placeholder="leer = keins"></div></div>
<label class="check"><input type="checkbox" name="encrypt_dirnames" {{ "checked" if job.encrypt_dirnames is not sameas false }}> Ordnernamen ebenfalls verschlüsseln</label>
<label class="check"><input type="checkbox" name="encrypt_ack"> Ich habe das Passwort sicher aufbewahrt und weiß: ohne Passwort sind die Daten verloren.</label>
<div class="hint">Passwort, zweites Passwort und Art der Namen lassen sich später nicht mehr ändern. Unverschlüsselte Dateien, die schon im Ziel liegen, bleiben dort liegen; lösche sie bei Bedarf selbst.</div>{% endif %}
</div>
{% if job.encrypt and job_id %}<div class="hint" id="encoff" style="display:none;margin-top:8px">Ausgeschaltet spiegelt der nächste Lauf wieder unverschlüsselt in das Ziel. Der verschlüsselte Ordner <code>data</code> wird dabei als überzählig gelöscht (Löschwarnung und Papierkorb greifen wie sonst). Der verschlüsselte Speicherort <code>{{ enc_remote }}</code> bleibt unter Speicherorte erhalten.</div>{% endif %}
</fieldset>
<script>function encShow(){const on=document.getElementById('enc').checked;document.getElementById('encbox').style.display=on?'':'none';const o=document.getElementById('encoff');if(o)o.style.display=on?'none':''}</script>
</div>

{% set sc_ok = can("jobs.scripts") %}<div class="card" id="scripts"><h2>Skripte, Snapshot und Wake-on-LAN</h2>
{% if not sc_ok %}<div class="msg info">Zum Ändern fehlt dir das Recht „Skripte, Snapshots und Wake-on-LAN einrichten“.</div>{% endif %}
<fieldset {{ "disabled" if not sc_ok }}>
<h3>Wake-on-LAN</h3>
<div class="row"><div style="flex:1 1 220px"><label for="wol_mac">MAC-Adresse des Zielservers</label><input type="text" name="wol_mac" id="wol_mac" value="{{ job.wol_mac or '' }}" placeholder="aus, z. B. AA:BB:CC:DD:EE:FF"></div>
<div style="flex:1 1 200px"><label for="wol_broadcast">Broadcast-Adresse</label><input type="text" name="wol_broadcast" id="wol_broadcast" value="{{ job.wol_broadcast or '' }}" placeholder="255.255.255.255"></div>
<div style="flex:0 0 110px"><label for="wol_port">Port</label><input type="text" inputmode="numeric" name="wol_port" id="wol_port" value="{{ job.wol_port or '' }}" placeholder="9"></div>
<div style="flex:0 0 160px"><label for="wol_wait">Warten bis (s)</label><input type="text" inputmode="numeric" name="wol_wait" id="wol_wait" value="{{ job.wol_wait or '' }}" placeholder="300"></div></div>
<div class="row"><div style="flex:1 1 260px"><label for="wol_check">Wach, wenn erreichbar (Host:Port)</label><input type="text" name="wol_check" id="wol_check" value="{{ job.wol_check or '' }}" placeholder="automatisch: Host des Ziels"></div>
<div style="flex:1 1 260px"><label for="wol_sleep_host">Schlafen legen über</label><select name="wol_sleep_host" id="wol_sleep_host"><option value="">Ziel (wenn SFTP)</option>{% for r in ssh_remotes %}<option value="{{ r }}" {{ "selected" if job.wol_sleep_host == r }}>{{ r }} (SSH)</option>{% endfor %}</select></div>
<div style="flex:1 1 260px"><label for="wol_sleep_cmd">Befehl zum Schlafenlegen</label><input type="text" name="wol_sleep_cmd" id="wol_sleep_cmd" value="{{ job.wol_sleep_cmd or '' }}" placeholder="systemctl suspend"></div></div>
<label class="check"><input type="checkbox" name="wol_sleep" {{ "checked" if job.wol_sleep }}> Nach dem Lauf wieder schlafen legen (nur, wenn MirrorSync ihn geweckt hat und keine andere Aufgabe ihn noch braucht)</label>
<div class="hint">Vor dem Lauf prüft MirrorSync, ob das Ziel erreichbar ist, sonst schickt es ein Magic Packet und wartet. Das Paket muss den Server im LAN erreichen: mit macvlan oder <code>network_mode: host</code> klappt das direkt, im Bridge-Netz die Broadcast-Adresse des LANs eintragen (z. B. 192.168.1.255) oder einen WoL-Proxy nutzen. Schlafenlegen läuft per SSH über einen SFTP-Speicherort; der Benutzer braucht dafür das Recht (z. B. <code>sudo</code> ohne Passwort für <code>systemctl suspend</code>).</div>

<h3 style="margin-top:18px">Skripte vor und nach dem Lauf</h3>
<div class="row"><div style="flex:1 1 260px"><label for="script_host">Ausführen</label><select name="script_host" id="script_host"><option value="">im MirrorSync-Container</option>{% for r in ssh_remotes %}<option value="{{ r }}" {{ "selected" if job.script_host == r }}>auf {{ r }} (SSH)</option>{% endfor %}</select></div>
<div style="flex:0 0 200px"><label for="script_timeout">Zeitlimit je Skript (s)</label><input type="text" inputmode="numeric" name="script_timeout" id="script_timeout" value="{{ job.script_timeout or '' }}" placeholder="600"></div></div>
<label for="script_pre">Vor dem Lauf</label><textarea name="script_pre" id="script_pre" rows="3" spellcheck="false" placeholder="z. B. docker stop nextcloud-db">{{ job.script_pre or '' }}</textarea>
<div class="row"><div style="flex:0 0 360px"><label for="script_pre_fail">Wenn das Skript fehlschlägt</label><select name="script_pre_fail" id="script_pre_fail"><option value="abort" {{ "selected" if job.script_pre_fail != "continue" }}>Lauf abbrechen</option><option value="continue" {{ "selected" if job.script_pre_fail == "continue" }}>trotzdem spiegeln</option></select></div></div>
<label for="script_post">Nach dem Lauf</label><textarea name="script_post" id="script_post" rows="3" spellcheck="false" placeholder="z. B. docker start nextcloud-db">{{ job.script_post or '' }}</textarea>
<div class="row"><div style="flex:0 0 360px"><label for="script_post_when">Ausführen</label><select name="script_post_when" id="script_post_when"><option value="always" {{ "selected" if (job.script_post_when or "always") == "always" }}>immer (auch nach Fehler)</option><option value="ok" {{ "selected" if job.script_post_when == "ok" }}>nur nach Erfolg</option><option value="fail" {{ "selected" if job.script_post_when == "fail" }}>nur nach Fehler</option></select></div></div>
<div class="hint">Shell-Befehle (<code>sh</code>), eine oder mehrere Zeilen. Verfügbar sind <code>$MS_JOB_NAME</code>, <code>$MS_SOURCE</code>, <code>$MS_DEST</code>, <code>$MS_RUN_ID</code> und nach dem Lauf <code>$MS_STATUS</code> (ok oder fehler). Ausgabe und Exit-Code stehen im Log. Per SSH gelten Host, Benutzer und Passwort bzw. Schlüssel des SFTP-Speicherorts. Die Skripte laufen nur bei echten Läufen, nicht bei Testläufen und Live-Runden. Das Skript danach läuft nach Prüflauf und Snapshot.</div>

<h3 style="margin-top:18px">Snapshot am Ziel nach jedem Lauf</h3>
<div class="row"><div style="flex:0 0 260px"><label for="snapshot">Art</label><select name="snapshot" id="snapshot" onchange="snapShow()">
<option value="off" {{ "selected" if (job.snapshot or "off") == "off" }}>aus</option><option value="zfs" {{ "selected" if job.snapshot == "zfs" }}>ZFS</option>
<option value="btrfs" {{ "selected" if job.snapshot == "btrfs" }}>Btrfs</option><option value="command" {{ "selected" if job.snapshot == "command" }}>eigener Befehl</option></select></div>
<div style="flex:1 1 260px" class="snap-on"><label for="snapshot_host">Ausführen</label><select name="snapshot_host" id="snapshot_host"><option value="">im MirrorSync-Container</option>{% for r in ssh_remotes %}<option value="{{ r }}" {{ "selected" if job.snapshot_host == r }}>auf {{ r }} (SSH)</option>{% endfor %}</select></div>
<div style="flex:0 0 200px" class="snap-on"><label for="snapshot_keep">Snapshots behalten</label><input type="text" inputmode="numeric" name="snapshot_keep" id="snapshot_keep" value="{{ job.snapshot_keep or '' }}" placeholder="alle"></div></div>
<div class="row snap-fs"><div><label for="snapshot_target" id="snaplbl">ZFS-Dataset bzw. Btrfs-Subvolume</label><input type="text" name="snapshot_target" id="snapshot_target" value="{{ job.snapshot_target or '' }}" placeholder="tank/backup  bzw.  /mnt/backup"></div>
<div class="snap-btrfs"><label for="snapshot_dir">Ordner für die Snapshots (Btrfs)</label><input type="text" name="snapshot_dir" id="snapshot_dir" value="{{ job.snapshot_dir or '' }}" placeholder="/mnt/snapshots"></div></div>
<div class="snap-cmd"><label for="snapshot_cmd">Befehl</label><input type="text" name="snapshot_cmd" id="snapshot_cmd" value="{{ job.snapshot_cmd or '' }}" placeholder="z. B. /usr/local/bin/snap.sh {name}"></div>
<label class="check snap-fs"><input type="checkbox" name="snapshot_sudo" {{ "checked" if job.snapshot_sudo }}> Mit <code>sudo -n</code> ausführen</label>
<div class="hint snap-on">Nach jedem erfolgreichen echten Lauf entsteht ein Snapshot <code>mirrorsync-&lt;Aufgabe&gt;-&lt;Datum&gt;</code>, so kommst du jederzeit auf den Stand von gestern zurück. „Behalten“ räumt nur Snapshots von MirrorSync auf. Btrfs-Snapshots müssen außerhalb des Ziels liegen, sonst würden sie beim nächsten Lauf als fremde Dateien gelöscht. Im eigenen Befehl stehen <code>{name}</code>, <code>{date}</code>, <code>{job}</code> und <code>{dest}</code> zur Verfügung. Schlägt der Snapshot fehl, gilt der Lauf als Fehler.</div>
</fieldset>
<script>function snapShow(){const v=document.getElementById('snapshot').value;
document.querySelectorAll('.snap-on').forEach(e=>e.style.display=v==='off'?'none':'');
document.querySelectorAll('.snap-fs').forEach(e=>e.style.display=(v==='zfs'||v==='btrfs')?'':'none');
document.querySelectorAll('.snap-btrfs').forEach(e=>e.style.display=v==='btrfs'?'':'none');
document.querySelectorAll('.snap-cmd').forEach(e=>e.style.display=v==='command'?'':'none')}snapShow()</script>
</div>

</fieldset>{% if editable %}<div style="display:flex;gap:8px;align-items:center;justify-content:space-between;flex-wrap:wrap">
<div><button class="btn pri">Speichern</button> <a class="btn" href="/">Abbrechen</a>
{% if job_id and job.direction == "bisync" and can("jobs.run") %} <button class="btn" type="submit" form="resyncform" title="Beide Seiten neu zusammenführen (--resync), gelöscht wird dabei nichts">Neu zusammenführen</button>{% endif %}</div>
{% if job_id and can("jobs.delete") %}<button class="btn del" type="submit" form="delform">Aufgabe entfernen</button>{% endif %}
</div>{% else %}<a class="btn" href="/">Zurück</a>{% endif %}
</form>
{% if job_id %}<form id="delform" method="post" action="/job/{{ job_id }}/delete" onsubmit="return confirm('Aufgabe entfernen? (Dateien bleiben unberührt)')"></form>
<form id="resyncform" method="post" action="/job/{{ job_id }}/resync" onsubmit="return confirm('Beide Seiten neu zusammenführen? Was nur auf einer Seite liegt, wird auf die andere kopiert. Gelöscht wird nichts.')"></form>{% endif %}
<script>
function nshow(){const m=document.getElementById('nmode').value;
document.querySelectorAll('.ncustom').forEach(e=>e.style.display=m==='custom'?'':'none');
document.querySelectorAll('.nglobal').forEach(e=>e.style.display=m==='global'?'':'none');
document.querySelectorAll('.ntexts').forEach(e=>e.style.display=m==='off'?'none':'');}
nshow();
async function ntest(){const out=document.getElementById('nres');out.textContent='Sende…';out.className='hint';
  try{const r=await (await fetch('{{ "/job/" ~ job_id ~ "/notify-test" if job_id else "/job/notify-test" }}',{method:'POST',body:new FormData(document.getElementById('jobform')),headers:{Accept:'application/json'}})).json();
  if(r.error){out.textContent=r.error;out.className='hint fehler';return}
  const names={webhook:'Webhook',smtp:'E-Mail',telegram:'Telegram',apprise:'Apprise'};
  out.innerHTML=Object.entries(r.results).map(([k,v])=>v===null?'<span class="ok">✓ '+names[k]+'</span>':'<span class="fehler">✗ '+names[k]+': '+v.replace(/</g,'&lt;')+'</span>').join(' &nbsp; ');
  }catch(e){out.textContent='Fehler: '+e;out.className='hint fehler'}}
</script>
<script>
function baseName(src){let p=src.trim().replace(/\/+$/,'');if(!p.startsWith('/')&&p.includes(':'))p=p.slice(p.indexOf(':')+1);return p.replace(/^\/+/,'')?p.split('/').pop():''}
function destPreview(){const ic=document.getElementById('incdir'),hasSel=fbEl('selection').value.split('\n').some(x=>x.trim()&&!x.trim().startsWith('#'));
  if(hasSel&&!ic.disabled){ic.dataset.was=ic.checked?'1':'';ic.checked=false;ic.disabled=true}else if(!hasSel&&ic.disabled){ic.disabled=false;ic.checked=ic.dataset.was==='1'}
  document.getElementById('incoff').style.display=hasSel?'':'none';
  const s=document.getElementById('source').value.trim(),d=document.getElementById('dest').value.trim(),inc=ic.checked,el=document.getElementById('destprev');
  if(!s||!d){el.textContent='';return}
  const n=baseName(s);
  if(inc&&!n){el.innerHTML='<span class="fehler">Geht nicht: Die Quelle ist die oberste Ebene eines Speicherorts.</span>';return}
  const target=inc?((d.endsWith('/')||d.endsWith(':'))?d+n:d+'/'+n):d;
  const sel=fbEl('selection').value.split('\n').map(x=>x.trim()).filter(x=>x&&!x.startsWith('#'));
  const fmt=(t,...a)=>t.replace(/\{(\d)\}/g,(m,i)=>a[+i]);
  if(isTW()){if(sel.length){el.innerHTML=fmt('Ergebnis: Nur <b>{0}</b> aus „{1}“ werden mit <code>{2}</code> abgeglichen, in beide Richtungen. Alles andere bleibt auf beiden Seiten unberührt.',sel.length===1?'„'+esc(sel[0])+'“':fmt('{0} ausgewählte Einträge',sel.length),esc(n||s),esc(target));return}
    el.innerHTML=inc?fmt('Ergebnis: Seite B ist der Ordner <code>{1}</code>. „{0}“ und <code>{1}</code> werden in beide Richtungen abgeglichen.',esc(n),esc(target))
     :fmt('Ergebnis: „{0}“ und <code>{1}</code> werden in beide Richtungen abgeglichen. Mit Häkchen wäre Seite B <code>{2}</code>.',esc(n||s),esc(target),esc(((d.endsWith('/')||d.endsWith(':'))?d:d+'/')+(n||'…')));return}
  if(sel.length){el.innerHTML=fmt('Ergebnis: Nur <b>{0}</b> aus „{1}“ landen in <code>{2}</code>. Gelöscht wird dort nur innerhalb der Auswahl, alles andere im Ziel bleibt unberührt.',sel.length===1?'„'+esc(sel[0])+'“':fmt('{0} ausgewählte Einträge',sel.length),esc(n||s),esc(target));return}
  el.innerHTML=inc?fmt('Ergebnis: Der <b>Ordner „{0}“</b> wird angelegt als <code>{1}</code>. Gelöscht wird nur innerhalb von <code>{1}</code>.',esc(n),esc(target))
   :fmt('Ergebnis: Der <b>Inhalt von „{0}“</b> landet in <code>{1}</code>. Mit Häkchen wäre es <code>{2}</code>. Gelöscht wird nur innerhalb von <code>{1}</code>.',esc(n||s),esc(target),esc(((d.endsWith('/')||d.endsWith(':'))?d:d+'/')+(n||'…')));}
document.addEventListener('DOMContentLoaded',()=>{['source','dest','selection'].forEach(i=>document.getElementById(i).addEventListener('input',destPreview));destPreview()});
function joinPath(base,d){return (base.endsWith('/')||base.endsWith(':'))?base+d:base+'/'+d}
function upOf(p){p=p.replace(/\/+$/,'');if(!p)return null;
  if(/^[^\/]+:$/.test(p)||p==='/data'||p==='')return '';           // Speicherort-Wurzel -> Auswahl der Speicherorte
  const i=p.lastIndexOf('/');const c=p.indexOf(':');
  if(i>c&&i>0){const u=p.slice(0,i);return u.endsWith(':')?u+'/':(u||'/')}   // eine Ebene hoch (name:/opt -> name:/)
  return c>=0?p.slice(0,c+1):'';}
function row(box,html,fn,title){const e=document.createElement('div');e.innerHTML=html;if(title)e.title=title;if(fn)e.onclick=fn;else e.style.cursor='default';box.append(e);return e}
const esc=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
/* ---------- Datei-Browser (Seitenpanel rechts) ---------- */
const FB={mode:null,path:'',data:null,sort:{k:'name',d:1},req:0,root:'',sel:new Map()};
function splitP(p){if(p.startsWith('/'))return ['/',p.slice(1)];const i=p.indexOf(':');const b=p.slice(0,i+1)+(p.slice(i+1).startsWith('/')?'/':'');return [b,p.slice(b.length)]}
function segsOf(p){return splitP(p)[1].split('/').filter(Boolean)}
function selInit(){FB.sel=new Map();const src=fbEl('source').value.trim();if(!src)return;
  fbEl('selection').value.split('\n').map(x=>x.trim()).filter(x=>x&&!x.startsWith('#')).forEach(l=>{const d=l.endsWith('/');l=l.replace(/^\/+|\/+$/g,'');if(l)FB.sel.set(joinPath(src.replace(/\/+$/,'')||src,l),d)})}
function selResult(){/* Basisordner + relative Auswahl; aktuelle Quelle bleibt Basis, wenn alles darin liegt */
  const items=[...FB.sel].map(([f,d])=>({b:splitP(f)[0],segs:segsOf(f),d}));if(!items.length)return null;
  const b=items[0].b;if(items.some(x=>x.b!==b))return {error:'Alle markierten Einträge müssen auf demselben Speicherort liegen.'};
  let common=null;const src=fbEl('source').value.trim();
  if(src&&splitP(src)[0]===b){const ss=segsOf(src);if(items.every(x=>x.segs.length>ss.length&&ss.every((s,i)=>x.segs[i]===s)))common=ss}
  if(!common){common=items[0].segs.slice(0,-1);items.forEach(x=>{let i=0;while(i<common.length&&i<x.segs.length-1&&common[i]===x.segs[i])i++;common=common.slice(0,i)})}
  const base=common.length?b+common.join('/'):b;
  return {base,sel:items.map(x=>x.segs.slice(common.length).join('/')+(x.d?'/':''))}}
const fmtSize=n=>{if(n==null)return '';const u=['B','KB','MB','GB','TB'];let i=0;while(n>=1024&&i<4){n/=1024;i++}return (i?n.toFixed(n<10?1:0):n)+' '+u[i]};
const fmtDt=s=>s?s.slice(8,10)+'.'+s.slice(5,7)+'.'+s.slice(0,4)+' '+s.slice(11,16):'';
function fbEl(id){return document.getElementById(id)}
function openFB(mode){const src=fbEl('source').value.trim();
  if(mode==='ex'&&!src){alert('Bitte zuerst die Quelle eintragen.');return}
  FB.mode=mode;FB.root=mode==='ex'?src.replace(/\/+$/,'')||src:'';if(mode==='source')selInit();
  fbEl('fbtitle').textContent=mode==='source'?'Quelle wählen':mode==='dest'?'Ziel wählen':'Ausschlüsse wählen';
  fbEl('fbq').value='';document.body.classList.add('fb-open');fbEl('fbpanel').setAttribute('aria-hidden','false');
  const start=mode==='ex'?src:fbEl(mode).value.trim();fbLoad(start)}
function closeFB(){document.body.classList.remove('fb-open');fbEl('fbpanel').setAttribute('aria-hidden','true');FB.mode=null}
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&FB.mode)closeFB()});
function fbCrumbs(){const c=fbEl('fbcrumbs'),p=FB.path;const parts=[];
  if(FB.mode!=='ex')parts.push(['Speicherorte','']);
  if(p){let base,rest;
    if(p.startsWith('/')){base='/';rest=p.slice(1)}else{const i=p.indexOf(':');base=p.slice(0,i+1)+(p.slice(i+1).startsWith('/')?'/':'');rest=p.slice(base.length)}
    parts.push([base==='/'?'/':base,base]);let acc=base;
    rest.split('/').filter(Boolean).forEach(seg=>{acc=joinPath(acc,seg);parts.push([seg,acc])})}
  c.innerHTML='';parts.forEach(([l,pp],i)=>{if(i)c.append(Object.assign(document.createElement('span'),{className:'sep',textContent:'›'}));
    const inRoot=FB.mode!=='ex'||pp.replace(/\/+$/,'').length>=FB.root.length;
    const a=document.createElement(inRoot?'a':'span');a.textContent=l;if(inRoot){a.href='#';a.onclick=e=>{e.preventDefault();fbLoad(pp)}}else a.className='mut';c.append(a)})}
async function fbLoad(path){FB.path=path;FB.data=null;const my=++FB.req;fbCrumbs();fbEl('fbmsg').innerHTML='<div class="hint" style="padding:10px">Lade…</div>';fbEl('fbbody').innerHTML='';
  try{const url=path?'/browse/list?path='+encodeURIComponent(path):'/browse?path=';
    const r=await (await fetch(url,{headers:{Accept:'application/json'}})).json();if(my!==FB.req)return;
    if(path&&r.path&&r.path!==path){FB.path=r.path;fbCrumbs()}
    FB.data=r;fbEl('fbmsg').innerHTML=r.ok===false?'<div class="msg err">'+esc(r.error||'Fehler')+(r.detail?'<details><summary>Details</summary><pre>'+esc(r.detail)+'</pre></details>':'')+'</div>':'';fbRender()}
  catch(e){if(my===FB.req)fbEl('fbmsg').innerHTML='<div class="msg err">Keine Verbindung zum Server.</div>'}}
function relEx(full,dir){let x=full.slice(FB.root.length);x=x.startsWith('/')?x:'/'+x;return dir?x.replace(/\/?$/,'/'):x}
function fbRender(){const d=FB.data,tb=fbEl('fbbody'),q=fbEl('fbq').value.trim().toLowerCase();tb.innerHTML='';
  const foot=fbEl('fbfoot');
  if(!FB.path){ // Auswahl der Speicherorte
    fbEl('fbhead').style.display='none';
    (d.entries||[]).filter(e=>!q||e.name.toLowerCase().includes(q)).forEach(en=>{const tr=document.createElement('tr');tr.className='fdir';
      tr.innerHTML='<td><a href="#">'+(en.kind==='remote'?'🖧 ':'📂 ')+esc(en.name)+'</a></td><td class="mut" colspan="2">'+esc(en.type)+'</td>';
      tr.querySelector('a').onclick=e=>{e.preventDefault();fbLoad(en.path)};tb.append(tr)});
    if(!(d.entries||[]).length)tb.innerHTML='<tr><td colspan="3" class="mut" style="padding:14px">'+esc(d.hint||'Keine Speicherorte.')+' <a href="/remotes">Speicherorte</a></td></tr>';
    fbEl('fbsum').textContent='Speicherort wählen';foot.querySelector('.fbuse').style.display='none';return}
  fbEl('fbhead').style.display='';
  const rows=(d&&d.ok?d.entries:[]).filter(e=>!q||e.name.toLowerCase().includes(q));
  rows.sort((a,b)=>{if(a.dir!==b.dir)return a.dir?-1:1;const k=FB.sort.k;const x=a[k]??-1,y=b[k]??-1;
    return k==='name'?String(x).localeCompare(String(y),'de',{numeric:true,sensitivity:'base'})*FB.sort.d:(x<y?-1:x>y?1:0)*FB.sort.d});
  const up=upOf(FB.path);const atRoot=FB.mode==='ex'&&FB.path.replace(/\/+$/,'')===FB.root;
  if(up!==null&&!atRoot){const tr=document.createElement('tr');tr.className='fdir';tr.innerHTML='<td colspan="3"><a href="#">⬆ ..</a></td>';
    tr.querySelector('a').onclick=e=>{e.preventDefault();fbLoad(up)};tb.append(tr)}
  const ex=fbEl('excludes')?fbEl('excludes').value.split('\n').map(x=>x.trim()):[];
  rows.forEach(e=>{const full=joinPath(FB.path,e.name),tr=document.createElement('tr');tr.className=e.dir?'fdir':'ffile';
    const line=FB.mode==='ex'?relEx(full,e.dir):'';const done=FB.mode==='ex'&&ex.includes(line);
    const ck=FB.mode==='source'?'<input type="checkbox" class="fbck" title="nur diese Datei bzw. diesen Ordner synchronisieren"'+(FB.sel.has(full)?' checked':'')+'> ':'';
    tr.innerHTML='<td>'+ck+(FB.mode==='ex'?'<button type="button" class="btn sm exb'+(done?' on':'')+'" title="'+(done?'ist ausgeschlossen':'ausschließen')+'">⛔</button> ':'')+
      (e.dir?'<a href="#">📁 '+esc(e.name)+'</a>':'<span>📄 '+esc(e.name)+'</span>')+'<div class="mob mut">'+(e.dir?'':fmtSize(e.size)+' · ')+fmtDt(e.mod)+'</div></td>'+
      '<td class="num hide-sm">'+(e.dir?'':fmtSize(e.size))+'</td><td class="hide-sm"><small>'+fmtDt(e.mod)+'</small></td>';
    if(e.dir)tr.querySelector('a').onclick=ev=>{ev.preventDefault();fbLoad(full)};
    const b=tr.querySelector('.exb');if(b)b.onclick=()=>{const ta=fbEl('excludes');const lines=ta.value.split('\n').map(x=>x.trim()).filter(Boolean);
      const i=lines.indexOf(line);if(i>=0)lines.splice(i,1);else lines.push(line);ta.value=lines.join('\n');fbRender()};
    const c=tr.querySelector('.fbck');if(c){c.onchange=()=>{c.checked?FB.sel.set(full,e.dir):FB.sel.delete(full);fbRender()};if(c.checked)tr.classList.add('picked')}
    if(done)tr.classList.add('excluded');tb.append(tr)});
  if(d&&d.ok&&!rows.length)tb.insertAdjacentHTML('beforeend','<tr><td colspan="3" class="mut" style="padding:14px">'+(q?'Kein Treffer.':'Ordner ist leer.')+'</td></tr>');
  if(d&&d.ok){const nd=d.entries.filter(e=>e.dir).length,nf=d.entries.length-nd,sz=d.entries.reduce((a,e)=>a+(e.size||0),0);
    fbEl('fbsum').textContent=nd+' Ordner, '+nf+' Dateien'+(nf?' ('+fmtSize(sz)+')':'')+(q?' · '+rows.length+' Treffer':'')+(d.truncated?' · nur die ersten 5000 von '+d.total:'')}
  else fbEl('fbsum').textContent='';
  document.querySelectorAll('#fbt th[data-k]').forEach(th=>th.dataset.dir=th.dataset.k===FB.sort.k?(FB.sort.d>0?'▲':'▼'):'');
  const use=foot.querySelector('.fbuse');
  if(FB.mode==='ex'){use.style.display='none';fbEl('fbsum').textContent+=' · ⛔ schließt aus, nochmal klicken nimmt es wieder heraus'}
  else if(FB.mode==='source'&&FB.sel.size){use.style.display='';use.disabled=false;
    use.innerHTML=FB.sel.size===1?'Übernehmen: 1 Eintrag markiert':'Übernehmen: {0} Einträge markiert'.replace('{0}',FB.sel.size);
    fbEl('fbsum').innerHTML=esc(fbEl('fbsum').textContent)+' · <a href="#" onclick="event.preventDefault();FB.sel.clear();fbRender()">Häkchen entfernen</a>'}
  else{use.style.display='';use.innerHTML='Übernehmen: <code>'+esc(FB.path)+'</code>';use.disabled=!(d&&d.ok);
    if(FB.mode==='source')fbEl('fbsum').textContent+=' · ☑ markiert einzelne Dateien oder Ordner'}}
function fbUse(){const id=FB.mode;
  if(id==='source'){const r=selResult();
    if(r&&r.error){alert(r.error);return}
    fbEl('source').value=r?r.base:FB.path;fbEl('selection').value=r?r.sel.join('\n'):''}
  else fbEl(id).value=FB.path;
  fbEl(id).dispatchEvent(new Event('input'));destPreview();closeFB()}
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('#fbt th[data-k]').forEach(th=>th.onclick=()=>{FB.sort.k===th.dataset.k?FB.sort.d*=-1:(FB.sort={k:th.dataset.k,d:th.dataset.k==='name'?1:-1});fbRender()});
  fbEl('fbq').addEventListener('input',()=>FB.data&&fbRender())});
</script>
{% endblock %}""",

"log.html": r"""{% extends "base.html" %}{% block title %}{{ job.name }}{% endblock %}{% block subtitle %}<p class="path">{{ job.source }} {{ "⇄" if job.direction == "bisync" else "→" }} {{ job.dest }}</p>{% endblock %}
{% block actions %}{% if can("jobs.restore") and job.versioning %}<a class="btn" href="/job/{{ job_id }}/versions">🗑 Papierkorb</a>{% endif %}{% if can("jobs.preview") %}<a class="btn" href="/job/{{ job_id }}/usage">📊 Platzbedarf</a>{% endif %}{% endblock %}
{% block body %}{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}
{% if job.delete_hold %}{% set h = job.delete_hold %}<div class="card" style="border-color:var(--err)"><h2>🛑 Angehalten: Löschwarnung</h2>
<p>{{ _("{0} von {1} Dateien im Ziel würden gelöscht ({2} %, Grenze {3} %).", h.deleted, h.total, h.pct, h.threshold) }} {{ _("Festgestellt am {0}.", h.at|dt) }} Nichts wurde verändert. Das kann auf eine versehentlich leere Quelle, ein nicht eingehängtes Laufwerk oder Ransomware hindeuten.</p>
{% if h.examples %}<details><summary>Betroffene Dateien (Auszug)</summary><pre style="max-height:240px">{{ h.examples|join("\n") }}</pre></details>{% endif %}
{% if can("jobs.approve") and not running %}<p style="margin-bottom:0"><form class="inline" method="post" action="/job/{{ job_id }}/approve" data-q="{{ _('Wirklich freigeben? Der Lauf startet jetzt und löscht {0} Dateien im Ziel.', h.deleted) }}" onsubmit="return confirm(this.dataset.q)"><button class="btn del">Freigeben und jetzt spiegeln</button></form>
<form class="inline" method="post" action="/job/{{ job_id }}/hold/dismiss"><button class="btn">Warnung verwerfen (nächster Lauf prüft wieder)</button></form>
{% if can("jobs.preview") %}<a class="btn" href="/job/{{ job_id }}">Aufgabe öffnen (Vorschau)</a>{% endif %}</p>{% endif %}</div>{% endif %}
{% if job.retry_pending and not running %}<div class="msg info">↻ {{ _("Neuer Versuch {0} von {1} um {2}. Gemeldet wird erst, wenn auch der letzte scheitert.", job.retry_pending.attempt, job.retry_pending.of, job.retry_pending.at[11:16]) }}</div>{% endif %}
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
<h2 style="margin:0">{{ "Aktueller Lauf" if running else "Letzter Lauf" }} {% if running %}<span class="tag laeuft">läuft</span>{% endif %}</h2>
<div>{% if running %}{% if can("jobs.run") %}<form class="inline" method="post" action="/job/{{ job_id }}/stop"><button class="btn del">Stopp</button></form>{% endif %}
{% else %}{% if can("jobs.run") %}<form class="inline" method="post" action="/job/{{ job_id }}/run"><button class="btn pri">Jetzt spiegeln</button></form>{% endif %}
{% if can("jobs.dryrun") %}<form class="inline" method="post" action="/job/{{ job_id }}/run"><input type="hidden" name="dry" value="1"><button class="btn">Testlauf</button></form>{% endif %}
{% if can("jobs.run") %}<form class="inline" method="post" action="/job/{{ job_id }}/verify"><button class="btn" title="Quelle und Ziel vergleichen, ohne etwas zu ändern">🔎 Jetzt prüfen</button></form>{% endif %}{% endif %}
{% if current %}<a class="btn" href="/job/{{ job_id }}/run/{{ current }}">Ganzes Log mit Filter</a>{% endif %}
<a class="btn" href="/">Zurück</a></div></div>
<pre id="log">{{ log }}</pre>
</div>

<div class="card"><h2>Verlauf</h2>
<p class="hint" style="margin-top:-6px">Klick auf einen Lauf zeigt sein vollständiges Log. Aufbewahrt werden die letzten {{ keep_runs }} Läufe{% if keep_days %}, höchstens {{ keep_days }} Tage{% endif %}{% if can("system.settings") %} (<a href="/settings/general">ändern</a>){% endif %}.</p>
{% if job.history or running %}<table><tr><th>Start</th><th class="hide-sm">Dauer</th><th>Status</th><th title="kopiert">Kopiert</th><th title="gelöscht">Gelöscht</th><th>Fehler</th><th class="hide-sm">Gestartet von</th><th></th></tr>
{% if running and current %}<tr class="click" onclick="location='/job/{{ job_id }}/run/{{ current }}'"><td>jetzt</td><td class="hide-sm">–</td><td><span class="tag laeuft">läuft</span></td><td>–</td><td>–</td><td>–</td><td class="hide-sm">–</td><td><a class="btn sm" href="/job/{{ job_id }}/run/{{ current }}">Log</a></td></tr>{% endif %}
{% for h in job.history %}{% set ok = has_file.get(h.run) %}<tr {% if ok %}class="click" onclick="location='/job/{{ job_id }}/run/{{ h.run }}'"{% endif %}>
<td>{{ h.start }}</td><td class="hide-sm">{{ h.duration }} s</td>
<td><span class="tag {{ h.status }}">{{ STATUS.get(h.status, h.status) }}</span>{% if h.dry_run %} <small>Testlauf</small>{% endif %}{% if h.mode == "verify" %} <small>nur Prüflauf</small>{% endif %}{% if h.retry %} <small class="mut">↻ Versuch {{ h.retry }}</small>{% endif %}
{% if h.verify %}<br><small class="{{ 'ok' if h.verify.result == 'ok' else 'fehler' }}" title="{{ _('{0} gleich, {1} fehlen im Ziel, {2} nur im Ziel, {3} unterschiedlich', h.verify.matched, h.verify.missing, h.verify.extra, h.verify.differ) }}">{% if h.verify.result == "ok" %}✔ {{ _("1:1 gleich ({0} Dateien)", h.verify.matched) }}{% elif h.verify.result == "diff" %}✖ {{ _("{0} Abweichungen", h.verify.missing + h.verify.extra + h.verify.differ + h.verify.errors) }}{% else %}✖ Prüflauf fehlgeschlagen{% endif %}</small>{% endif %}
{% if h.hold %}<br><small class="fehler">🛑 {{ _("{0} % würden gelöscht", h.hold.pct) }}</small>{% endif %}{% if h.snapshot %}<br><small class="mut" title="{{ h.snapshot }}">📸 Snapshot</small>{% elif h.snapshot is defined %}<br><small class="fehler">📸 Snapshot fehlgeschlagen</small>{% endif %}{% if h.retry_next %}<br><small class="mut">↻ {{ _("nächster Versuch {0}", h.retry_next[11:16]) }}</small>{% endif %}{% if h.space_low %}<br><small class="fehler">💽 wenig Speicher</small>{% endif %}{% if h.window %}<br><small class="mut" title="{{ 'Geht im nächsten Zeitfenster weiter' if h.window == 'resume' else 'Am Ende des Zeitfensters angehalten' }}">🕘 Zeitfenster zu Ende</small>{% endif %}</td>
<td class="num" data-l="Kopiert">{{ h.copied if h.copied is defined else "–" }}</td><td class="num" data-l="Gelöscht">{{ h.deleted if h.deleted is defined else "–" }}</td>
<td class="num {{ 'err' if h.errors }}" data-l="Fehler">{{ h.errors if h.errors is defined else "–" }}</td>
<td class="hide-sm"><small>{{ h.by or "–" }}</small></td>
<td style="white-space:nowrap">{% if ok %}<a class="btn sm" href="/job/{{ job_id }}/run/{{ h.run }}">Log</a> <a class="btn sm hide-sm" href="/job/{{ job_id }}/run/{{ h.run }}/download" onclick="event.stopPropagation()" title="Herunterladen">↓</a>{% else %}<small class="mut">kein Log</small>{% endif %}</td></tr>{% endfor %}
</table>{% else %}<div class="empty">Noch kein Lauf.</div>{% endif %}
</div>
<script>const l=document.getElementById('log');l.scrollTop=l.scrollHeight</script>
{% endblock %}""",

"remotes.html": r"""{% extends "base.html" %}{% block title %}Speicherorte{% endblock %}{% block subtitle %}<p>Server und Clouds, zwischen denen gespiegelt wird.</p>{% endblock %}{% block actions %}{% if can("remotes.create") %}<a class="btn pri" href="/remotes/new">{{ ICON.plus }} Neuer Speicherort</a>{% endif %}{% endblock %}{% block body %}
{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
<div class="card">

{% if remotes %}<table><tr><th>Name</th><th>Typ</th><th class="hide-sm">Im Job verwenden als</th><th></th></tr>
{% for r in remotes %}<tr><td><b>{{ r.name }}</b>{% if r.no_token %}<br><span class="tag fehler">Anmeldung fehlt</span>{% endif %}</td><td>{{ r.type }}</td><td class="hide-sm"><code>{{ r.name }}:pfad/zum/ordner</code></td>
<td style="white-space:nowrap">{% if can("remotes.test") %}<form class="inline" method="post" action="/remotes/{{ r.name }}/test"><button class="btn sm">Testen</button></form>{% endif %}{% if can("remotes.edit") %}
{% if r.oauth %}<form class="inline" method="post" action="/remotes/{{ r.name }}/auth"><button class="btn sm {{ 'pri' if r.no_token }}">Anmelden</button></form>{% endif %}
<a class="btn sm" href="/remotes/{{ r.name }}/edit">Bearbeiten</a>{% endif %}{% if can("remotes.create") %}
<details class="pausemenu"><summary class="btn sm" title="Kopie mit denselben Zugangsdaten anlegen">⧉ Duplizieren</summary><div class="pmenu">
<b><span>Kopie von</span> {{ r.name }}</b><form method="post" action="/remotes/{{ r.name }}/duplicate" style="display:flex;gap:6px;margin-top:6px"><input type="text" name="new_name" value="{{ r.name }}-kopie" required pattern="[A-Za-z0-9_\-]+" style="height:30px;width:170px" aria-label="Neuer Name"><button class="btn sm pri">Anlegen</button></form>
<div class="hint">Name nur aus Buchstaben, Ziffern, - und _. Passwort und Anmeldung werden mitkopiert.</div></div></details>{% endif %}{% if can("remotes.delete") %}
<form class="inline" method="post" action="/remotes/{{ r.name }}/delete" onsubmit="return confirm('Speicherort {{ r.name }} entfernen?')"><button class="btn sm del">Entfernen</button></form>{% endif %}</td></tr>
{% endfor %}</table>{% else %}<div class="empty">Noch keine Speicherorte angelegt.</div>{% endif %}
<p class="hint" style="padding:0 10px 8px">Alle rclone-Speicherarten werden unterstützt (SMB, WebDAV, SFTP, FTP, S3, B2, Azure, Google Drive, OneDrive, Dropbox, pCloud, MEGA, crypt und rund 45 weitere).
Lokale Ordner brauchen keinen Eintrag: Sie werden in der docker-compose.yml unter <code>/data</code> eingebunden.</p>
</div>
{% endblock %}""",

"preview_page.html": r"""{% extends "base.html" %}{% block title %}Vorschau: Ziel nach dem Lauf{% endblock %}
{% block subtitle %}<p>So sieht das Ziel nach dem nächsten Lauf aus. Nur zum Ansehen, es wird nichts kopiert oder gelöscht.</p>{% endblock %}
{% block actions %}{% if job_id %}<a class="btn" href="/job/{{ job_id }}">Zur Aufgabe</a>{% endif %}{% endblock %}
{% block body %}
<style>
.fm{padding:14px}.fm-head{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.fm-crumb{font-family:var(--mono,monospace);font-size:13px;word-break:break-all;margin:6px 0}.fm-crumb a{cursor:pointer;color:var(--acc)}
.fm-tools{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0;align-items:center}.fm-tools input{height:32px;width:min(240px,50vw);margin-left:auto}
.fm table{width:100%}.fm td,.fm th{padding:6px 8px;vertical-align:middle}.fm td.nw,.fm th.nw{white-space:nowrap}
.fm .nm{overflow-wrap:anywhere;min-width:140px}.fm tr.d .nm{cursor:pointer}.fm tr.d .nm:hover{color:var(--acc)}
.fm .ico{display:inline-block;width:18px;vertical-align:-3px;margin-right:4px}.fm .ico svg{width:16px;height:16px}
.fm-scroll{overflow:auto;min-height:220px;max-height:calc(100vh - 330px);border:1px solid var(--bd);border-radius:8px}
.fm .st{font-size:12px;white-space:nowrap;margin-left:8px}.st.s-new{color:var(--ok)}.st.s-update{color:var(--run,#2563eb)}.st.s-delete{color:var(--err)}.st.s-to_a{color:var(--warn,#d97706)}
.fm tr.s-delete td.nm{text-decoration:line-through;opacity:.7}.fm-sum span{margin-right:14px;white-space:nowrap}
</style>
{% if err %}<div class="msg err">{{ err }}</div>{% else %}
<div class="card fm" id="fm">
<div class="fm-head"><b>Ziel</b> <code>{{ data.dest }}</code>{% if data.dest_missing %} <span class="tag">wird angelegt</span>{% endif %}
{% if data.mode == "bisync" %}<span class="tag">Zwei-Wege</span>{% endif %}<span style="flex:1"></span>
<label class="check" style="margin:0"><input type="checkbox" id="mark" onchange="R.render()"> Änderungen markieren</label></div>
<div class="fm-sum mut" style="font-size:13px"><span>{{ data.summary.files.new }} <span>neu</span></span><span>{{ data.summary.files["update"] }} <span>werden aktualisiert</span></span><span>{{ data.summary.files.delete }} <span>werden gelöscht</span></span>{% if data.mode == "bisync" %}<span>{{ data.summary.files.to_a }} <span>kommen nach A</span></span>{% endif %}<span>{{ data.summary.files.same }} <span>bleiben gleich</span></span></div>
{% if data.truncated %}<div class="hint">Sehr viele Dateien: Einzeln gezeigt werden nur die ersten Dateien, die Zähler an den Ordnern stimmen trotzdem.</div>{% endif %}
<div class="fm-crumb"></div>
<div class="fm-tools"><button type="button" class="btn sm" id="upbtn" onclick="R.up_()">Nach oben</button><input type="text" id="q" placeholder="Im Ordner suchen" autocomplete="off" oninput="R.render()"></div>
<div class="hint" id="outnote" style="display:none;margin:0 0 6px">Außerhalb des Ziels: so, wie es jetzt ist. Die Aufgabe ändert hier nichts.</div>
<div class="fm-scroll"><table><thead><tr><th>Name</th><th class="nw">Größe</th><th class="hide-sm nw">Geändert</th><th class="hide-sm nw">Rechte</th></tr></thead><tbody></tbody></table></div>
<p class="hint" style="margin:8px 0 0">Ordner anklicken zum Öffnen. Ohne „Änderungen markieren“ siehst du das Ziel genau so, wie es nach dem Lauf aussieht: Was gelöscht wird, fehlt.</p>
</div>
{% include "pv_up.html" %}<script>
const I_DIR={{ ICON.folder|tojson }},TREE={{ data.tree|tojson }},DEST={{ data.dest|tojson }},DS=PVUP.split(DEST);
const LBL={new:'neu',update:'wird aktualisiert',delete:'wird gelöscht',to_a:'kommt nach A',same:''};
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function fmt(b){const u=['B','KB','MB','GB','TB'];let i=0;while(b>=1024&&i<4){b/=1024;i++}return (i?b.toFixed(b<10?1:0):b)+' '+u[i]}
function dt(s){return s?s.slice(0,10)+' '+s.slice(11,16):''}
function strip(n){if(!n.d)return n;const c=Object.assign({},n.c,{delete:0}),b=Object.assign({},n.b,{delete:0});return Object.assign({},n,{c,b,ch:n.ch.filter(k=>k.s!=='delete').map(strip)})}
const R={path:[],up:null,
 root(){return document.getElementById('mark').checked?TREE:strip(TREE)},
 node(){let n=this.root(),ok=[];for(const p of this.path){const k=n.ch.find(x=>x.d&&x.n===p);if(!k)break;n=k;ok.push(p)}this.path=ok;return n},
 abs(){return this.up!==null?this.up:DS.segs.concat(this.path)},
 set(a){if(PVUP.isPrefix(DS.segs,a)){this.up=null;this.path=a.slice(DS.segs.length)}else this.up=a;document.getElementById('q').value='';this.render()},
 up_(){const a=this.abs();if(a.length&&(this.up!==null||this.path.length||PVUP.can))this.set(a.slice(0,-1))},
 go(i){this.set(this.abs().slice(0,i))},
 crumb(){const a=this.abs(),dl=DS.segs.length;let h='<a data-i="0">'+esc(DS.base)+'</a>';
  a.forEach((p,i)=>{h+=(i?'/':'')+'<a data-i="'+(i+1)+'">'+esc(p)+'</a>'+(i===dl-1?' 🎯':'')});
  const c=document.querySelector('.fm-crumb');c.innerHTML=h;c.querySelectorAll('a').forEach(x=>x.onclick=()=>this.go(+x.dataset.i));
  document.getElementById('upbtn').disabled=!(a.length&&(this.up!==null||this.path.length||PVUP.can));
  document.getElementById('outnote').style.display=this.up!==null?'':'none'},
 async renderUp(){const up=this.up,my=this.req=(this.req||0)+1,tb=document.querySelector('#fm tbody');this.crumb();
  tb.innerHTML='<tr><td colspan="4" class="mut">'+'Lade…'+'</td></tr>';
  const r0=await PVUP.list(PVUP.join(DS.base,up));if(my!==this.req)return;const r=PVUP.onWay(r0,up,DS.segs);
  if(r.ok===false){tb.innerHTML='<tr><td colspan="4"><div class="msg err" style="margin:0">'+esc(r.error||'Fehler')+'</div></td></tr>';return}
  const q=document.getElementById('q').value.trim().toLowerCase(),rows=PVUP.rows(r,up,DS.segs).filter(k=>!q||k.n.toLowerCase().includes(q));
  if(!rows.length){tb.innerHTML='<tr><td colspan="4" class="mut">'+'Ordner ist leer.'+'</td></tr>';return}
  tb.innerHTML=rows.map((k,i)=>'<tr class="'+(k.d?'d':'')+'" data-i="'+i+'"><td class="nm"><span class="ico">'+(k.d?I_DIR:'')+'</span>'+esc(k.n)+PVUP.tag(k)+'</td><td class="nw">'+(k.d||k.size==null?'<span class="mut">–</span>':fmt(k.size))+'</td><td class="hide-sm nw"><small>'+(k.mod?esc(k.mod.slice(0,16)):'<span class="mut">–</span>')+'</small></td><td class="hide-sm nw"><small><span class="mut">–</span></small></td></tr>').join('');
  tb.querySelectorAll('tr.d').forEach(tr=>tr.querySelector('.nm').onclick=()=>this.set(up.concat([rows[+tr.dataset.i].n])))},
 render(){if(this.up!==null){this.renderUp();return}const mark=document.getElementById('mark').checked,n=this.node(),q=document.getElementById('q').value.trim().toLowerCase();
  this.crumb();
  const rows=n.ch.filter(k=>!q||k.n.toLowerCase().includes(q)),tb=document.querySelector('#fm tbody');
  if(!rows.length){tb.innerHTML='<tr><td colspan="4" class="mut">'+'Ordner ist leer.'+'</td></tr>';return}
  tb.innerHTML=rows.map((k,i)=>{const st=mark&&LBL[k.s]?'<span class="st s-'+k.s+'">'+LBL[k.s]+'</span>':'';
   if(k.d){const b=k.b,c=k.c,sz=b.new+b.update+b.same+b.to_a+(mark?b.delete:0),cnt=c.new+c.update+c.same+c.to_a+(mark?c.delete:0);
    return '<tr class="d s-'+(mark?k.s:'same')+'" data-i="'+i+'"><td class="nm"><span class="ico">'+I_DIR+'</span>'+esc(k.n)+st+'</td><td class="nw">'+fmt(sz)+'<br><small class="mut">'+cnt+' '+'Dateien'+'</small></td><td class="hide-sm nw"><span class="mut">–</span></td><td class="hide-sm nw"><span class="mut">–</span></td></tr>'}
   return '<tr class="s-'+(mark?k.s:'same')+'"><td class="nm"><span class="ico"></span>'+esc(k.n)+st+'</td><td class="nw">'+fmt(k.size||0)+'</td><td class="hide-sm nw"><small>'+(k.m?esc(dt(k.m)):'<span class="mut">–</span>')+'</small></td><td class="hide-sm nw"><small><span class="mut" title="'+'Die Vorschau kennt keine Berechtigungen.'+'">–</span></small></td></tr>'}).join('');
  tb.querySelectorAll('tr.d').forEach(tr=>tr.querySelector('.nm').onclick=()=>this.set(this.abs().concat([rows[+tr.dataset.i].n])))}};
R.render();
</script>{% endif %}
{% endblock %}""",

"pv_up.html": r"""{# Vorschau: oberhalb des Ziels bis zum Stammverzeichnis gehen (echte Ordner, nur lesen) #}
<script>
const PVUP={can:{{ can("remotes.browse")|tojson }},cache:{},
 split(dest){dest=(dest||'').replace(/\/+$/,'');let base,rest;
  if(dest.startsWith('/')){base='/';rest=dest.slice(1)}else{const i=dest.indexOf(':');base=dest.slice(0,i+1)+(dest.slice(i+1).startsWith('/')?'/':'');rest=dest.slice(base.length)}
  return {base,segs:rest.split('/').filter(Boolean)}},
 join(base,segs){return base+segs.join('/')},
 isPrefix(a,b){return a.length<=b.length&&a.every((x,i)=>x===b[i])},
 async list(path){if(this.cache[path])return this.cache[path];
  try{const r=await (await fetch('/browse/list?path='+encodeURIComponent(path),{headers:{Accept:'application/json'}})).json();if(r.ok!==false)this.cache[path]=r;return r}
  catch(e){return {ok:false,error:'Keine Verbindung zum Server.'}}},
 /* Zeilen fuer einen Ordner oberhalb/neben dem Ziel: echte Eintraege, der Weg zum Ziel markiert */
 rows(r,up,destSegs){const out=(r.entries||[]).map(e=>({n:e.name,d:e.dir,size:e.size,mod:e.mod}));
  if(this.isPrefix(up,destSegs)&&up.length<destSegs.length){const nx=destSegs[up.length];let t=out.find(x=>x.d&&x.n===nx);
   if(!t){t={n:nx,d:true,size:null,mod:'',missing:true};out.push(t)}t.goal=up.length===destSegs.length-1?'dest':'way'}
  out.sort((a,b)=>a.d!==b.d?(a.d?-1:1):a.n.localeCompare(b.n,'de',{numeric:true,sensitivity:'base'}));return out},
 onWay(r,up,segs){return r.ok===false&&this.isPrefix(up,segs)?{ok:true,entries:[]}:r},
 tag(x){return x.goal==='dest'?' <span class="tag ok">'+'🎯 Ziel der Aufgabe'+'</span>'+(x.missing?' <span class="tag">'+'wird angelegt'+'</span>':''):x.goal==='way'?' <span class="tag">'+'→ zum Ziel'+'</span>'+(x.missing?' <span class="tag">'+'wird angelegt'+'</span>':''):''},
 note:'Außerhalb des Ziels: so, wie es jetzt ist. Die Aufgabe ändert hier nichts.'};
</script>""",

"files.html": r"""{% extends "base.html" %}{% block title %}Dateien{% endblock %}
{% block subtitle %}<p>In einem oder zwei Speicherorten browsen, bearbeiten, kopieren und verschieben.</p>{% endblock %}
{% block body %}
<style>
.fm-wrap{display:grid;grid-template-columns:minmax(0,1fr);gap:16px;align-items:start}.fm-wrap.dual{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}.fm{min-width:0}
@media(max-width:1100px){.fm-wrap.dual{grid-template-columns:1fr}}
.fm{padding:14px}.fm-head{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.fm-head select{width:auto;min-width:200px}.fm-crumb{font-family:var(--mono,monospace);font-size:13px;word-break:break-all;margin:6px 0}
.fm-crumb a{cursor:pointer;color:var(--acc)}.fm-tools{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.fm table{width:100%}.fm td,.fm th{padding:6px 8px;vertical-align:middle}.fm tr.sel td{background:var(--acc-soft)}
.fm .nm{cursor:pointer;overflow-wrap:anywhere;min-width:140px}.fm td.nw,.fm th.nw{white-space:nowrap}.fm .nm:hover{color:var(--acc)}.fm .ico{display:inline-block;width:18px;vertical-align:-3px;margin-right:4px}
.fm .ico svg{width:16px;height:16px}.fm .acts{white-space:nowrap;text-align:right;width:1%}.fmmenu{position:relative;display:inline-block}.fmmenu>summary{list-style:none;cursor:pointer;padding:2px 10px;border:1px solid var(--bd2);border-radius:6px;font-weight:700}.fmmenu>summary::-webkit-details-marker{display:none}.fmmenu>div{position:absolute;right:0;top:calc(100% + 4px);z-index:30;background:var(--card);border:1px solid var(--bd);border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.18);padding:4px;min-width:170px;display:flex;flex-direction:column}.fmmenu>div>*{text-align:left;background:none;border:0;padding:7px 10px;border-radius:6px;color:var(--fg);cursor:pointer;font:inherit;text-decoration:none}.fmmenu>div>*:hover{background:var(--acc-soft)}.fmmenu>div>div.mut:hover{background:none}.fmmenu>div>hr{border:0;border-top:1px solid var(--bd);margin:4px 2px;padding:0;border-radius:0}
.fm-scroll{overflow:auto;min-height:220px;border:1px solid var(--bd);border-radius:8px}
.fmprog{padding:10px 14px}.fmprow{display:flex;gap:12px;align-items:center;padding:6px 0;border-bottom:1px solid var(--bd)}.fmprow:last-child{border-bottom:0}
.fmpt{flex:1;min-width:0;overflow-wrap:anywhere}.fmpc{white-space:nowrap;min-width:56px;text-align:right}.fmpbar{flex:0 0 min(320px,30vw);height:10px;background:var(--bd);border-radius:5px;overflow:hidden}
.fmpbar i{display:block;height:100%;background:var(--acc);transition:width .4s}.fmprow.tot{border-bottom:2px solid var(--bd2)}
@media(max-width:700px){.fmprow{flex-wrap:wrap}.fmpbar{flex:1 1 100%}}
.fm-dlg{border:1px solid var(--bd);border-radius:12px;background:var(--card);color:var(--fg);padding:18px;width:min(560px,94vw)}
.fm-dlg.big{width:min(1100px,96vw)}.fm-dlg::backdrop{background:rgba(0,0,0,.45)}
.fm-dlg textarea{width:100%;min-height:55vh;font-family:var(--mono,monospace);font-size:13px}
.fm-scroll.dropon{outline:2px dashed var(--acc);outline-offset:-2px;background:var(--acc-soft)}.fm tr.dropdir td{background:var(--acc-soft);box-shadow:inset 0 0 0 1px var(--acc)}.fm tr[draggable=true]{cursor:grab}
</style>
{% if not locations %}<div class="card"><div class="empty">Keine Speicherorte, die du sehen darfst. Unter <a href="/remotes">Speicherorte</a> anlegen.</div></div>{% else %}
<div class="card" style="padding:12px 14px"><label class="check" style="margin:0"><input type="checkbox" id="dualchk" onchange="setDual(this.checked)"> Zwei Speicherorte nebeneinander (Kopieren und Verschieben zwischen beiden)</label></div>
<div class="card fmprog" id="fmprog" hidden></div>
<div class="fm-wrap" id="fmwrap">
{% for side in ["a", "b"] %}<div class="card fm" id="fm_{{ side }}" {{ 'style=display:none' if side == "b" }}>
<div class="fm-head"><b>{{ "Links" if side == "a" else "Rechts" }}</b><select class="loc" onchange="P.{{ side }}.open(this.value,'')">{% for l in locations %}<option value="{{ l.id }}">{{ l.label }} ({{ l.type }})</option>{% endfor %}</select>
<button type="button" class="btn sm" onclick="P.{{ side }}.reload()">Neu laden</button></div>
<div class="fm-crumb"></div>
<div class="fm-tools">
<button type="button" class="btn sm" onclick="P.{{ side }}.up()">Nach oben</button>
{% if can("files.edit") %}<button type="button" class="btn sm" onclick="P.{{ side }}.mkdir()">{{ ICON.plus }} Ordner</button>
<button type="button" class="btn sm" onclick="P.{{ side }}.newfile()">{{ ICON.plus }} Datei</button>
<label class="btn sm" style="margin:0;cursor:pointer">Hochladen<input type="file" multiple style="display:none" onchange="P.{{ side }}.upload(this)"></label>{% endif %}
<button type="button" class="btn sm" onclick="P.{{ side }}.sizeAll()">Ordnergrößen</button>
<span class="mut selinfo" style="align-self:center;font-size:13px"></span>
{% if can("files.edit") %}<button type="button" class="btn sm sa" onclick="P.{{ side }}.transfer(false,true)">Kopieren nach …</button>
{% if can("files.delete") %}<button type="button" class="btn sm sa" onclick="P.{{ side }}.transfer(true,true)">Verschieben nach …</button>{% endif %}
<button type="button" class="btn sm sa other" onclick="P.{{ side }}.transfer(false,false)">{{ "Nach rechts kopieren →" if side == "a" else "← Nach links kopieren" }}</button>
{% if can("files.delete") %}<button type="button" class="btn sm sa other" onclick="P.{{ side }}.transfer(true,false)">{{ "Nach rechts verschieben →" if side == "a" else "← Nach links verschieben" }}</button>{% endif %}{% endif %}
{% if can("files.delete") %}<button type="button" class="btn sm del sa" onclick="P.{{ side }}.del()">Löschen</button>{% endif %}
</div>
<div class="fm-scroll"><table><thead><tr><th style="width:26px"><input type="checkbox" class="all" onchange="P.{{ side }}.selAll(this.checked)"></th><th>Name</th><th class="nw">Größe</th><th class="hide-sm nw">Geändert</th><th class="hide-sm nw">Rechte</th><th></th></tr></thead><tbody></tbody></table></div>
<div class="hint foot"></div>
{% if can("files.edit") %}<div class="hint">Dateien und Ordner vom Computer hierher ziehen lädt sie hoch. Zeilen auf die andere Seite ziehen kopiert sie (mit gedrückter Umschalttaste verschieben), auf einen Ordner ziehen legt sie dort hinein.</div>{% endif %}
<div class="hint">Rechtsklick auf einen Eintrag oder auf die freie Fläche öffnet ein Menü mit allen Aktionen.</div>
</div>{% endfor %}
</div>
{% endif %}
<div class="fmmenu" id="ctxmenu" style="position:fixed;display:none;z-index:95"><div style="position:static"></div></div>
<dialog class="fm-dlg" id="dlg_ask"><form method="dialog" onsubmit="return false"><h3 class="t" style="margin-top:0"></h3><input type="text" class="v" style="width:100%"><div class="hint h"></div>
<p style="margin-top:14px"><button type="button" class="btn pri ok">OK</button> <button type="button" class="btn no">Abbrechen</button></p></form></dialog>
<dialog class="fm-dlg big" id="dlg_edit"><h3 class="t" style="margin-top:0"></h3><textarea spellcheck="false"></textarea>
<p style="margin-top:12px">{% if can("files.edit") %}<button type="button" class="btn pri" onclick="saveEdit()">Speichern</button> {% endif %}<button type="button" class="btn" onclick="this.closest('dialog').close()">Schließen</button> <span class="mut st"></span></p></dialog>
<dialog class="fm-dlg" id="dlg_info"><h3 class="t" style="margin-top:0">Eigenschaften</h3><table class="b"></table><div class="hint h"></div>
<p style="margin-top:12px"><button type="button" class="btn" onclick="this.closest('dialog').close()">Schließen</button></p></dialog>
<script>
const LOCS={{ locations|tojson }}, CAN_EDIT={{ 'true' if can("files.edit") else 'false' }}, CAN_DEL={{ 'true' if can("files.delete") else 'false' }};
const I_DIR={{ ICON.folder|tojson }};
const esc=t=>String(t??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=n=>{if(n==null)return '';const u=['B','KB','MB','GB','TB'];let i=0;while(n>=1024&&i<4){n/=1024;i++}return (i?n.toFixed(1):n)+' '+u[i]};
const fill=(s,...a)=>a.reduce((x,v,i)=>x.split('{'+i+'}').join(v),s);
let DUAL=false;
async function op(name,body){
  const r=await fetch('/files/op/'+name,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(body)});
  let d={};try{d=await r.json()}catch(e){d={ok:false,error:'Fehler'}}
  d.status=r.status;return d;
}
function ask(title,val,hint){return new Promise(res=>{const d=document.getElementById('dlg_ask');d.querySelector('.t').textContent=title;
  const v=d.querySelector('.v');v.value=val||'';d.querySelector('.h').textContent=hint||'';
  const done=x=>{d.close();res(x)};d.querySelector('.ok').onclick=()=>done(v.value.trim());d.querySelector('.no').onclick=()=>done(null);
  v.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();done(v.value.trim())}};d.oncancel=()=>res(null);d.showModal();v.focus();v.select();});}
function joinp(a,b){return a?(b?a+'/'+b:a):b}
class Pane{
  constructor(side){this.side=side;this.el=document.getElementById('fm_'+side);this.loc=LOCS[0].id;this.path='';this.entries=[];this.sel=new Set();this.dnd();this.el.querySelector('.fm-scroll').addEventListener('contextmenu',ev=>this.ctx(ev));}
  other(){return this.side==='a'?P.b:P.a}
  async open(loc,path){this.loc=loc;this.path=path||'';this.sel.clear();this.el.querySelector('.loc').value=loc;await this.reload();saveState();}
  async reload(){const tb=this.el.querySelector('tbody');tb.innerHTML='<tr><td colspan="6" class="mut">'+'Lädt …'+'</td></tr>';
    const d=await op('list',{loc:this.loc,path:this.path});
    if(!d.ok){tb.innerHTML='<tr><td colspan="6"><div class="msg err" style="margin:0">'+esc(d.error)+(d.detail?'<br><small>'+esc(d.detail)+'</small>':'')+'</div></td></tr>';this.entries=[];this.crumb();this.tools();return}
    this.entries=d.entries;this.sel.clear();this.render();
    this.el.querySelector('.foot').textContent=d.truncated?fill('Nur die ersten {0} von {1} Einträgen.',d.entries.length,d.total):'';fitPanes();}
  crumb(){const c=this.el.querySelector('.fm-crumb');const parts=this.path?this.path.split('/'):[];
    let h='<a data-p="">'+esc(this.loc.replace(/:$/,''))+':/</a>';let acc='';
    parts.forEach(p=>{acc=joinp(acc,p);h+='<a data-p="'+esc(acc)+'">'+esc(p)+'</a>/'});c.innerHTML=h;
    c.querySelectorAll('a').forEach(a=>a.onclick=()=>this.open(this.loc,a.dataset.p));}
  render(){this.crumb();const tb=this.el.querySelector('tbody');
    if(!this.entries.length){tb.innerHTML='<tr><td colspan="6" class="mut">'+'Ordner ist leer.'+'</td></tr>';this.tools();return}
    tb.innerHTML=this.entries.map((e,i)=>'<tr data-i="'+i+'" class="'+(this.sel.has(e.name)?'sel':'')+'"><td><input type="checkbox" '+(this.sel.has(e.name)?'checked':'')+'></td>'+
      '<td class="nm"><span class="ico">'+(e.dir?I_DIR:'')+'</span>'+esc(e.name)+'</td>'+
      '<td class="sz nw">'+(e.dir?(e.dsize!=null?esc(fmt(e.dsize))+'<br><small class="mut">'+esc(e.dcount||'')+'</small>':'<button type="button" class="btn sm szb">'+'berechnen'+'</button>'):fmt(e.size))+'</td>'+
      '<td class="hide-sm nw"><small>'+(e.mod?esc(e.mod):'<span class="mut">–</span>')+'</small></td><td class="hide-sm nw"><small>'+(e.mode?'<code>'+esc(e.mode)+'</code>':'<span class="mut" title="'+esc('Dieser Speichertyp liefert keine Berechtigungen (z. B. SMB, WebDAV, Clouds).')+'">–</span>')+'</small></td>'+
      '<td class="acts"><details class="fmmenu"><summary title="Aktionen">⋯</summary><div><button type="button" class="inf">'+'Eigenschaften'+'</button>'+
      (e.dir?'<button type="button" class="op">'+'Öffnen'+'</button>':'<button type="button" class="ed">'+(CAN_EDIT?'Bearbeiten':'Ansehen')+'</button><a href="/files/download?loc='+encodeURIComponent(this.loc)+'&path='+encodeURIComponent(joinp(this.path,e.name))+'">'+'Herunterladen'+'</a>')+
      (CAN_EDIT?'<button type="button" class="rn">'+'Umbenennen'+'</button><button type="button" class="cp">'+'Kopieren nach …'+'</button>':'')+
      (CAN_EDIT&&CAN_DEL?'<button type="button" class="mv">'+'Verschieben nach …'+'</button>':'')+(CAN_DEL?'<button type="button" class="dl" style="color:var(--err)">'+'Löschen'+'</button>':'')+'</div></details></td></tr>').join('');
    tb.querySelectorAll('tr').forEach(tr=>{const e=this.entries[+tr.dataset.i];
      if(CAN_EDIT){tr.draggable=true;tr.addEventListener('dragstart',ev=>{const names=this.sel.has(e.name)?[...this.sel]:[e.name];
        DRAG={pane:this,loc:this.loc,path:this.path,names};ev.dataTransfer.setData('application/x-mirrorsync',names.join('\n'));ev.dataTransfer.effectAllowed='copyMove';});
        tr.addEventListener('dragend',()=>setTimeout(()=>{DRAG=null},0));}
      tr.querySelector('input').onchange=ev=>{ev.target.checked?this.sel.add(e.name):this.sel.delete(e.name);tr.classList.toggle('sel',ev.target.checked);this.tools()};
      tr.querySelector('.nm').onclick=()=>e.dir?this.open(this.loc,joinp(this.path,e.name)):this.edit(e);
      tr.querySelector('.inf').onclick=()=>this.info(e);
      const ed=tr.querySelector('.ed');if(ed)ed.onclick=()=>this.edit(e);
      const rn=tr.querySelector('.rn');if(rn)rn.onclick=()=>this.rename(e);
      const one=fn=>()=>{tr.querySelector('details').open=false;this.sel=new Set([e.name]);fn()};
      const q=(c,fn)=>{const x=tr.querySelector(c);if(x)x.addEventListener('click',one(fn))};
      q('.op',()=>this.open(this.loc,joinp(this.path,e.name)));q('.cp',()=>this.transfer(false,true));q('.mv',()=>this.transfer(true,true));q('.dl',()=>this.del());
      tr.querySelectorAll('.fmmenu>div>*').forEach(x=>x.addEventListener('click',()=>tr.querySelector('details').open=false));
      const sb=tr.querySelector('.szb');if(sb)sb.onclick=()=>this.dirSize(e,tr);});
    this.tools();}
  tools(){const n=this.sel.size;this.el.querySelectorAll('.sa').forEach(b=>b.style.display=n?'':'none');
    this.el.querySelectorAll('.other').forEach(b=>b.style.display=n&&DUAL?'':'none');
    this.el.querySelector('.selinfo').textContent=n?fill('{0} ausgewählt',n):'';this.el.querySelector('.all').checked=n&&n===this.entries.length;fitPanes();}
  selAll(on){this.sel=new Set(on?this.entries.map(e=>e.name):[]);this.render()}
  up(){if(!this.path)return;this.open(this.loc,this.path.split('/').slice(0,-1).join('/'))}
  async dirSize(e,tr){const c=tr.querySelector('.sz');c.textContent='…';const d=await op('size',{loc:this.loc,path:joinp(this.path,e.name)});
    if(d.ok){e.dsize=d.bytes;e.dcount=fill('{0} Ordner, {1} Dateien',d.dirs,d.files);c.innerHTML=esc(fmt(d.bytes))+'<br><small class="mut">'+esc(e.dcount)+'</small>'}else c.textContent=d.error;}
  async sizeAll(){const d=await op('size',{loc:this.loc,path:this.path});
    this.el.querySelector('.foot').textContent=d.ok?fill('Dieser Ordner: {0} in {1} Dateien und {2} Unterordnern.',fmt(d.bytes),d.files,d.dirs):d.error;
    for(const tr of this.el.querySelectorAll('tbody tr')){const e=this.entries[+tr.dataset.i];if(e&&e.dir&&e.dsize==null)await this.dirSize(e,tr)}}
  async info(e){const d=await op('info',{loc:this.loc,path:joinp(this.path,e.name)});const g=document.getElementById('dlg_info');
    const rows=d.ok?[['Pfad',d.display],['Typ',d.dir?'Ordner':'Datei'],['Größe',d.dir?(e.dsize!=null?fmt(e.dsize)+' · '+e.dcount:'–'):fmt(d.size)+' ('+d.size+' B)'],['Geändert',d.mod],
      ['Berechtigungen',d.mode?d.mode+' ('+(d.metadata.mode||'')+')':(e.mode||'–')],['Besitzer (uid:gid)',d.owner||e.owner||'–']]:[['Fehler',d.error]];
    g.querySelector('.b').innerHTML=rows.map(r=>'<tr><th style="text-align:left;padding-right:14px">'+esc(r[0])+'</th><td><code>'+esc(r[1])+'</code></td></tr>').join('');
    g.querySelector('.h').textContent=d.hint||'';g.showModal();}
  async edit(e){const d=await op('read',{loc:this.loc,path:joinp(this.path,e.name)});if(!d.ok){alertMsg(d.error);return}
    const g=document.getElementById('dlg_edit');g.querySelector('.t').textContent=joinp(this.path,e.name);g.querySelector('textarea').value=d.content;
    g.querySelector('textarea').readOnly=!CAN_EDIT;g.querySelector('.st').textContent='';EDIT={pane:this,path:joinp(this.path,e.name)};g.showModal();}
  async mkdir(){const n=await ask('Neuer Ordner','','Name des Ordners');if(!n)return;const d=await op('mkdir',{loc:this.loc,path:this.path,name:n});if(!d.ok)alertMsg(d.error);this.refreshBoth();}
  async newfile(){const n=await ask('Neue Datei','neu.txt','Leere Textdatei, danach im Editor bearbeiten.');if(!n)return;
    const d=await op('write',{loc:this.loc,path:this.path,name:n,content:''});if(!d.ok){alertMsg(d.error);return}await this.reload();this.edit({name:n});}
  async rename(e){const n=await ask(fill('„{0}“ umbenennen',e.name),e.name);if(!n||n===e.name)return;
    const d=await op('rename',{loc:this.loc,path:joinp(this.path,e.name),new_name:n});if(!d.ok)alertMsg(d.error);this.refreshBoth();}
  async upload(inp){const files=[...inp.files].map(f=>({file:f,dir:''}));inp.value='';await this.uploadList(files,this.path);}
  async uploadList(items,base){const foot=this.el.querySelector('.foot');let mode=null;let n=0;
    for(const it of items){n++;if(it.mkdir){const parts=it.mkdir.split('/');const nm=parts.pop();await op('mkdir',{loc:this.loc,path:joinp(base,parts.join('/')),name:nm});continue}
      const dir=joinp(base,it.dir);let ow=mode==='all';for(;;){
      foot.textContent=fill('Lade {0} hoch …',joinp(it.dir,it.file.name))+(items.length>1?' ('+n+'/'+items.length+')':'');
      const fd=new FormData();fd.append('loc',this.loc);fd.append('path',dir);fd.append('overwrite',ow?'1':'');fd.append('file',it.file);
      const r=await fetch('/files/upload',{method:'POST',body:fd,headers:{'Accept':'application/json'}});let d={};try{d=await r.json()}catch(e){d={ok:false,error:'Fehler'}}
      if(r.status===409&&d.exists&&!ow){if(mode==='skip')break;
        if(items.length>1){mode=confirm(fill('„{0}“ gibt es schon. Alle vorhandenen Dateien überschreiben?',joinp(it.dir,it.file.name))+'\n\n'+'OK = überschreiben, Abbrechen = vorhandene überspringen.')?'all':'skip';if(mode==='skip')break;ow=true;continue}
        if(confirm(fill('„{0}“ gibt es schon. Überschreiben?',it.file.name))){ow=true;continue}break}
      if(!d.ok)alertMsg(d.error);break}}
    foot.textContent='';this.refreshBoth();}
  ctx(ev){const sc=this.el.querySelector('.fm-scroll');if(!sc.contains(ev.target))return;ev.preventDefault();
    const row=ev.target.closest('tr[data-i]');const e=row&&this.entries[+row.dataset.i];
    if(e&&!this.sel.has(e.name)){this.sel=new Set([e.name]);this.render()}
    if(!e&&this.sel.size){this.sel.clear();this.render()}
    const n=this.sel.size, one=n===1?this.entries.find(x=>x.name===[...this.sel][0]):null, other=this.side==='a'?'rechts':'links';
    const items=[];const add=(label,fn,cls)=>items.push([label,fn,cls]);const sep=()=>items.push(null);
    if(!n){if(CAN_EDIT){add('Neuer Ordner',()=>this.mkdir());add('Neue Datei',()=>this.newfile());add('Hochladen',()=>this.el.querySelector('input[type=file]').click());sep()}
      add('Neu laden',()=>this.reload());add('Ordnergrößen',()=>this.sizeAll());if(this.path)add('Nach oben',()=>this.up());if(this.entries.length)add('Alle auswählen',()=>this.selAll(true));}
    else{if(one){if(one.dir)add('Öffnen',()=>this.open(this.loc,joinp(this.path,one.name)));else{add(CAN_EDIT?'Bearbeiten':'Ansehen',()=>this.edit(one));
          add('Herunterladen',()=>{location.href='/files/download?loc='+encodeURIComponent(this.loc)+'&path='+encodeURIComponent(joinp(this.path,one.name))})}
        add('Eigenschaften',()=>this.info(one));if(one.dir)add('Größe berechnen',()=>{const tr=[...this.el.querySelectorAll('tbody tr')].find(t=>this.entries[+t.dataset.i]===one);if(tr)this.dirSize(one,tr)});
        if(CAN_EDIT)add('Umbenennen',()=>this.rename(one));sep()}
      else{add(fill('{0} ausgewählt',n),null,'mut');sep()}
      if(CAN_EDIT){add('Kopieren nach …',()=>this.transfer(false,true));if(CAN_DEL)add('Verschieben nach …',()=>this.transfer(true,true));
        if(DUAL){add(this.side==='a'?'Nach rechts kopieren →':'← Nach links kopieren',()=>this.transfer(false,false));if(CAN_DEL)add(this.side==='a'?'Nach rechts verschieben →':'← Nach links verschieben',()=>this.transfer(true,false))}}
      if(CAN_DEL){sep();add('Löschen',()=>this.del(),'danger')}
      sep();add('Auswahl aufheben',()=>this.selAll(false));}
    showCtx(ev.clientX,ev.clientY,items);}
  dnd(){const el=this.el, sc=el.querySelector('.fm-scroll');
    const over=(on)=>sc.classList.toggle('dropon',on);
    sc.addEventListener('dragover',ev=>{const t=ev.dataTransfer.types;if(!CAN_EDIT||!(t.includes('Files')||t.includes('application/x-mirrorsync')))return;ev.preventDefault();
      const row=ev.target.closest('tr[data-i]');sc.querySelectorAll('tr.dropdir').forEach(x=>x!==row&&x.classList.remove('dropdir'));
      const e=row&&this.entries[+row.dataset.i];if(e&&e.dir)row.classList.add('dropdir');over(true);
      ev.dataTransfer.dropEffect=t.includes('Files')?'copy':(ev.shiftKey||(DRAG&&DRAG.pane===this)?'move':'copy');});
    sc.addEventListener('dragleave',ev=>{if(!sc.contains(ev.relatedTarget)){over(false);sc.querySelectorAll('tr.dropdir').forEach(x=>x.classList.remove('dropdir'))}});
    sc.addEventListener('drop',async ev=>{ev.preventDefault();over(false);const row=ev.target.closest('tr[data-i]');sc.querySelectorAll('tr.dropdir').forEach(x=>x.classList.remove('dropdir'));
      const e=row&&this.entries[+row.dataset.i];const target=e&&e.dir?joinp(this.path,e.name):this.path;
      if(ev.dataTransfer.types.includes('application/x-mirrorsync')){const src=DRAG;DRAG=null;if(!src)return;
        const same=src.pane===this;const move=same||ev.shiftKey;
        if(same&&target===this.path)return;
        if(move&&!CAN_DEL){alertMsg('Verschieben braucht zusätzlich das Recht „Dateien löschen“.');return}
        if(src.names.some(n=>same&&joinp(src.path,n)===target))return;
        const what=src.names.length===1?src.names[0]:fill('{0} Einträge',src.names.length);
        if(!confirm(fill(move?'{0} nach „{1}“ verschieben?':'{0} nach „{1}“ kopieren?',what,(this.loc.replace(/:$/,''))+':/'+target)))return;
        const body={loc:src.loc,paths:src.names.map(n=>joinp(src.path,n)),dst_loc:this.loc,dst_path:target};
        let d=await op(move?'move':'copy',body);
        if(d.status===409&&d.exists){if(!confirm(d.error))return;body.overwrite=true;d=await op(move?'move':'copy',body)}
        if(!d.ok){alertMsg(d.error);return}src.pane.sel.clear();src.pane.tools();(window.msPoll&&msPoll());return}
      const items=await dropItems(ev.dataTransfer);if(items.length)await this.uploadList(items,target);});}
  async del(){const names=[...this.sel];if(!names.length)return;
    if(!confirm(fill('{0} Einträge endgültig löschen? Ordner werden mit ihrem ganzen Inhalt gelöscht.',names.length)+'\n\n'+names.slice(0,15).join('\n')+(names.length>15?'\n…':'')))return;
    const d=await op('delete',{loc:this.loc,paths:names.map(n=>joinp(this.path,n)),confirm:true});if(!d.ok)alertMsg(d.error);this.refreshBoth();}
  async transfer(move,ask_dst){const names=[...this.sel];if(!names.length)return;let dloc=this.loc,dpath=this.path;
    if(!ask_dst){const o=this.other();dloc=o.loc;dpath=o.path}
    else{const v=await ask(move?'Verschieben nach':'Kopieren nach',this.path,'Zielordner in diesem Speicherort, z. B. Ordner/Unterordner. Leer = oberste Ebene.');if(v===null)return;dpath=v.replace(/^\/+|\/+$/g,'')}
    const body={loc:this.loc,paths:names.map(n=>joinp(this.path,n)),dst_loc:dloc,dst_path:dpath};
    let d=await op(move?'move':'copy',body);
    if(d.status===409&&d.exists){if(!confirm(d.error))return;body.overwrite=true;d=await op(move?'move':'copy',body)}
    if(!d.ok){alertMsg(d.error);return}this.sel.clear();this.tools();if(window.msPoll)msPoll();}
  refreshBoth(){this.reload();const o=this.other();if(DUAL&&o.loc===this.loc)o.reload()}
}
let EDIT=null, DRAG=null;
function showCtx(x,y,items){const m=document.getElementById('ctxmenu'),box=m.firstElementChild;box.innerHTML='';
  items.forEach((it,i)=>{if(!it){if(box.lastElementChild&&box.lastElementChild.tagName!=='HR')box.append(document.createElement('hr'));return}
    const b=document.createElement(it[1]?'button':'div');b.type='button';b.textContent=it[0];if(it[2]==='danger')b.style.color='var(--err)';if(it[2]==='mut'){b.className='mut';b.style.cursor='default'}
    if(it[1])b.onclick=()=>{hideCtx();it[1]()};box.append(b)});
  if(box.lastElementChild&&box.lastElementChild.tagName==='HR')box.lastElementChild.remove();
  m.style.display='block';const r=box.getBoundingClientRect();m.style.left=Math.min(x,innerWidth-r.width-8)+'px';m.style.top=Math.min(y,innerHeight-r.height-8)+'px';}
function hideCtx(){document.getElementById('ctxmenu').style.display='none'}
document.addEventListener('click',ev=>{if(!ev.target.closest('#ctxmenu'))hideCtx()});
document.addEventListener('keydown',ev=>{if(ev.key==='Escape')hideCtx()});
window.addEventListener('scroll',hideCtx,true);window.addEventListener('blur',hideCtx);
async function dropItems(dt){const out=[];const entries=[...dt.items].map(i=>i.webkitGetAsEntry&&i.webkitGetAsEntry()).filter(Boolean);
  if(!entries.length){[...dt.files].forEach(f=>out.push({file:f,dir:''}));return out}
  const fileOf=en=>new Promise((res,rej)=>en.file(res,rej));
  const readAll=rd=>new Promise(res=>{const all=[];const step=()=>rd.readEntries(b=>{if(!b.length)return res(all);all.push(...b);step()},()=>res(all));step()});
  async function walk(en,dir){if(en.isFile){try{out.push({file:await fileOf(en),dir})}catch(e){}}
    else if(en.isDirectory){const sub=joinp(dir,en.name);const kids=await readAll(en.createReader());if(!kids.length)out.push({mkdir:sub});for(const k of kids)await walk(k,sub)}}
  for(const en of entries)await walk(en,'');
  return out}
async function saveEdit(){const g=document.getElementById('dlg_edit');const st=g.querySelector('.st');st.textContent='Speichert …';
  const d=await op('write',{loc:EDIT.pane.loc,path:EDIT.path,content:g.querySelector('textarea').value,overwrite:true});
  st.textContent=d.ok?'Gespeichert.':d.error;if(d.ok)EDIT.pane.refreshBoth();}
function alertMsg(t){const f=document.querySelector('main');const m=document.createElement('div');m.className='msg err';m.textContent=t;f.prepend(m);setTimeout(()=>m.remove(),8000);window.scrollTo(0,0)}
const P={a:new Pane('a'),b:new Pane('b')};
function setDual(on){DUAL=on;document.getElementById('fm_b').style.display=on?'':'none';document.getElementById('fmwrap').classList.toggle('dual',on);
  if(on&&!P.b.entries.length)P.b.open(P.b.loc,P.b.path);P.a.tools();P.b.tools();saveState();fitPanes();}
function saveState(){const q=new URLSearchParams({a:P.a.loc,ap:P.a.path});if(DUAL){q.set('b',P.b.loc);q.set('bp',P.b.path)}history.replaceState(null,'','/files?'+q)}
window.onTasksDone=()=>{P.a.reload();if(DUAL)P.b.reload()};
/* Gesamtfortschritt laufender (und gerade fertiger) Kopier- und Verschiebe-Auftraege direkt auf der Seite */
const PROG_SEEN={};
window.onTasksUpdate=tasks=>{const box=document.getElementById('fmprog');const now=Date.now();
  const show=tasks.filter(t=>{if(t.state==='läuft'){PROG_SEEN[t.id]=now;return true}return PROG_SEEN[t.id]&&now-PROG_SEEN[t.id]<8000});
  if(!show.length){box.hidden=true;return}box.hidden=false;
  const run=show.filter(t=>t.state==='läuft');let h='';
  if(run.length>1){const bt=run.every(t=>t.bytes_total!=null)?run.reduce((a,t)=>a+t.bytes_total,0):null,bd=run.reduce((a,t)=>a+(t.bytes_done||0),0);
    const pc=bt?Math.min(99,Math.floor(bd*100/bt)):Math.round(run.reduce((a,t)=>a+(t.progress||0),0)/run.length);
    h+='<div class="fmprow tot"><div class="fmpt"><b>'+'Gesamt'+'</b> <span class="mut">'+fill('{0} Aufträge',run.length)+'</span><br><small class="mut">'+(bt!=null?esc(msB(bd)+' '+'von'+' '+msB(bt)):'')+'</small></div><b class="fmpc">'+pc+' %</b><div class="fmpbar"><i style="width:'+pc+'%"></i></div></div>'}
  h+=show.map(t=>{const pc=t.state==='ok'?100:(t.progress||0),col={'läuft':'var(--acc)','ok':'var(--ok)','fehler':'var(--err)','abgebrochen':'var(--mut)'}[t.state];
    return '<div class="fmprow"><div class="fmpt"><b>'+(t.op==='move'?'Verschieben':'Kopieren')+'</b> '+esc(t.label)+'<br><small class="mut">'+esc(msTaskLine(t)||t.stats||'')+'</small>'+(t.error?'<br><small style="color:var(--err)">'+esc(t.error)+'</small>':'')+'</div>'+
      '<b class="fmpc" style="color:'+col+'">'+(t.state==='läuft'?pc+' %':({'ok':'fertig','fehler':'Fehler','abgebrochen':'abgebrochen'}[t.state]))+'</b><div class="fmpbar"><i style="width:'+pc+'%;background:'+col+'"></i></div>'+
      (t.state==='läuft'&&CAN_EDIT?'<button type="button" class="btn sm" data-pc="'+esc(t.id)+'">'+'Abbrechen'+'</button>':'')+'</div>'}).join('');
  box.innerHTML=h;box.querySelectorAll('[data-pc]').forEach(x=>x.onclick=async()=>{await op('cancel',{task_id:x.dataset.pc});window.msPoll&&window.msPoll()})};
function fitPanes(){document.querySelectorAll('.fm-scroll').forEach(sc=>{if(!sc.offsetParent)return;const card=sc.closest('.fm');
  const bottom=card.getBoundingClientRect().bottom+window.scrollY, h=sc.getBoundingClientRect().height;
  sc.style.height=Math.max(220,Math.round(h-(bottom-(window.innerHeight-16))))+'px'})}
window.addEventListener('resize',fitPanes);
document.addEventListener('click',ev=>document.querySelectorAll('.fmmenu[open]').forEach(d=>{if(!d.contains(ev.target))d.open=false}));
if(LOCS.length){const q=new URLSearchParams(location.search);const ok=v=>LOCS.some(l=>l.id===v);
  P.a.loc=ok(q.get('a'))?q.get('a'):LOCS[0].id;P.a.path=q.get('ap')||'';P.b.loc=ok(q.get('b'))?q.get('b'):(LOCS[1]||LOCS[0]).id;P.b.path=q.get('bp')||'';
  P.a.open(P.a.loc,P.a.path);if(q.get('b')){document.getElementById('dualchk').checked=true;setDual(true)}fitPanes();}
</script>
{% endblock %}""",

"remote_edit.html": r"""{% extends "base.html" %}{% block title %}{{ name if name else "Neuer Speicherort" }}{% endblock %}{% block subtitle %}<p>{{ "Speicherort bearbeiten" if name else "Zugangsdaten für einen Server oder Cloud-Dienst" }}</p>{% endblock %}{% block body %}
<div class="card">
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
<form method="post" id="rf">
<div class="row">
<div><label>Name</label><input type="text" name="name" value="{{ name or form.get('name','') }}" {{ "disabled" if name }} placeholder="z. B. nas" required>
<div class="hint">Im Job dann als <code>name:pfad</code> verwenden.</div></div>
<div><label>Typ</label><select name="type" id="type" onchange="render()"></select></div></div>
{% if name %}<div id="typewarn" class="msg err" style="display:none;margin-top:14px">Achtung: Du wechselst das Protokoll. Beim Speichern wird der Speicherort mit dem neuen Typ neu eingerichtet, alle Felder werden neu abgefragt und das Passwort muss neu eingegeben werden. Aufgaben, die ihn verwenden, behalten den Namen. Pfade können sich je nach Protokoll unterscheiden (z. B. SMB: <code>freigabe/ordner</code>, SFTP: <code>/pfad</code>). Schlägt die Einrichtung fehl, bleibt der alte Stand erhalten.</div>{% endif %}
<div id="oauth" class="msg info" style="display:none;margin-top:14px">Dieser Dienst nutzt eine Anmeldung im Browser. Nach dem Speichern führt dich der nächste Schritt durch die Anmeldung
(einmal <code>rclone authorize</code> auf deinem PC ausführen und das Ergebnis hier einfügen). Client-ID und Secret kannst du leer lassen.</div>
<div id="fields"></div>
<details style="margin-top:14px"><summary style="cursor:pointer">Erweiterte Optionen</summary><div id="adv"></div></details>
{% if name %}<p class="hint">Passwortfelder leer lassen, um das gespeicherte Passwort zu behalten.</p>{% endif %}
{% if can("remotes.edit") or not name %}{% with vis_what="remote", vis_nocard=true %}{% include "vis_picker.html" %}{% endwith %}{% endif %}
<p style="margin-top:20px"><button class="btn pri">{{ "Speichern" if name else "Weiter" }}</button> <a class="btn" href="/remotes">Abbrechen</a></p>
</form></div>
<script>
const P={{ providers|tojson }}, EX={{ (existing or {})|tojson }}, FORM={{ form|tojson if form else '{}' }}, EDIT={{ 'true' if name else 'false' }};
const DE={host:'Server (IP oder Name)',user:'Benutzer',pass:'Passwort',port:'Port',url:'URL',domain:'Domäne',vendor:'Anbieter',
 key_file:'Schlüsseldatei (z. B. /config/id_ed25519)',provider:'Anbieter',access_key_id:'Access Key ID',secret_access_key:'Secret Access Key',
 region:'Region',endpoint:'Endpoint',account:'Konto / Account',key:'Schlüssel',remote:'Darunterliegender Speicherort (z. B. nas:verschluesselt)',
 password:'Passwort',password2:'Salt-Passwort (optional)',client_id:'Client-ID (optional)',client_secret:'Client-Secret (optional)'};
const sel=document.getElementById('type');
function opt(v,t){const o=document.createElement('option');o.value=v;o.textContent=t;return o}
const g1=document.createElement('optgroup');g1.label='Häufig';const g2=document.createElement('optgroup');g2.label='Weitere';
P.forEach(p=>(p.common?g1:g2).append(opt(p.name,p.common?p.label:p.name+' – '+p.label.split('\n')[0].slice(0,70))));
sel.append(g1,g2); sel.value=EX.type||FORM.type||'smb';
function matches(o,prov){ if(!o.Provider) return true; let neg=o.Provider.startsWith('!'); const l=o.Provider.replace(/^!/,'').split(',');
  return neg? !l.includes(prov) : l.includes(prov); }
const KEEP=['host','user'];
function same(){return !EDIT||sel.value===EX.type}
function val(n){ if(('opt_'+n) in FORM) return FORM['opt_'+n]; if(!same()&&!KEEP.includes(n)) return ''; return EX[n]!==undefined?String(EX[n]):''; }
function field(o){
  const w=document.createElement('div'); w.dataset.provider=o.Provider||'';
  const l=document.createElement('label'); l.textContent=(DE[o.Name]||o.Help.split('\n')[0])+(o.Required?' *':''); w.append(l);
  let i;
  const ex=o.Examples||[];
  if(o.Type==='bool'){ i=document.createElement('select'); i.append(opt('','Standard ('+(o.DefaultStr||'false')+')'),opt('true','ja'),opt('false','nein')); }
  else if(ex.length && (o.Exclusive||o.Name==='provider')){ i=document.createElement('select'); i.append(opt('','– bitte wählen –'));
    ex.forEach(e=>i.append(opt(e.Value,e.Value+(e.Help?' – '+e.Help.split('\n')[0].slice(0,80):'')))); }
  else { i=document.createElement('input'); i.type=(o.IsPassword||(o.Sensitive&&/secret|pass|_key$/.test(o.Name)))?'password':'text'; i.autocomplete='off';
    i.placeholder=o.IsPassword&&EDIT&&same()?'(unverändert)':(o.DefaultStr||'');
    if(ex.length){const id='dl_'+o.Name+Math.random().toString(36).slice(2,6);const dl=document.createElement('datalist');dl.id=id;
      ex.forEach(e=>dl.append(opt(e.Value,e.Help?e.Help.split('\n')[0]:'')));w.append(dl);i.setAttribute('list',id);} }
  i.name='opt_'+o.Name; i.value=o.IsPassword?'':val(o.Name); if(o.Required && !(o.IsPassword&&EDIT&&same())) i.required=true;
  if(o.Name==='provider'){i.onchange=filter;i.oninput=filter;}
  w.append(i);
  const h=document.createElement('div'); h.className='hint'; const rest=o.Help.split('\n').slice(DE[o.Name]?0:1).join(' ').trim();
  h.textContent=rest.length>260?rest.slice(0,260)+'…':rest; if(rest) w.append(h);
  return w;
}
function filter(){
  const pv=(document.querySelector('[name=opt_provider]')||{}).value||'';
  document.querySelectorAll('#fields>div,#adv>div').forEach(w=>{
    const on=!w.dataset.provider||matches({Provider:w.dataset.provider},pv);
    w.style.display=on?'':'none'; w.querySelectorAll('input,select').forEach(i=>i.disabled=!on);});
}
function render(){
  const p=P.find(x=>x.name===sel.value); const F=document.getElementById('fields'), A=document.getElementById('adv'); F.innerHTML='';A.innerHTML='';
  document.getElementById('oauth').style.display=p.oauth?'block':'none';
  const tw=document.getElementById('typewarn');if(tw)tw.style.display=same()?'none':'block';
  p.options.forEach(o=>(o.Advanced?A:F).append(field(o)));
  // Neuer Speicherort: Standard-Port des Typs vorausfuellen (bleibt aenderbar)
  const po=document.querySelector('#fields [name=opt_port],#adv [name=opt_port]'), pd=(p.options.find(o=>o.Name==='port')||{}).DefaultStr;
  if(po && !same() && pd && (!EDIT||!('opt_port' in FORM))) po.value=pd;
  if(po && !EDIT && !po.value && pd) po.value=pd;
  const tl=document.querySelector('[name=opt_tls]');
  if(po && tl && sel.value==='ftp') tl.addEventListener('change',()=>{ if(['','21','990'].includes(po.value)) po.value=tl.value==='true'?'990':'21'; });
  filter();
}
render();
</script>
{% endblock %}""",

"remote_wizard.html": r"""{% extends "base.html" %}{% block title %}{{ name }} einrichten{% endblock %}{% block body %}
<div class="card">
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
<form method="post">
{% if q.Name == "config_token" %}
<p><b>Anmeldung bei {{ typ }}</b>: Weil der Container keinen Browser hat, meldest du dich einmal an deinem PC an:</p>
<ol>
<li>rclone auf dem PC herunterladen (<a href="https://rclone.org/downloads/" target="_blank" rel="noopener">rclone.org/downloads</a>, einfach entpacken).</li>
<li>Im entpackten Ordner eine Eingabeaufforderung/Terminal öffnen und ausführen:<br>
<pre>{% set cmd = q.Help | regex_cmd %}{{ cmd or ('rclone authorize "' ~ typ ~ '"') }}</pre></li>
<li>Es öffnet sich der Browser, dort anmelden und Zugriff erlauben.</li>
<li>Im Terminal erscheint ein Block zwischen <code>---&gt;</code> und <code>&lt;---End paste</code>. Diesen Text (beginnt mit <code>{</code>) hier einfügen:</li>
</ol>
<textarea name="result" rows="5" required placeholder='{"access_token":"…","token_type":"Bearer","refresh_token":"…","expiry":"…"}'></textarea>
{% else %}
<pre style="white-space:pre-wrap">{{ q.Help }}</pre>
{% if q.Examples and q.Exclusive %}<select name="result">{% for e in q.Examples %}<option value="{{ e.Value }}" {{ "selected" if e.Value == q.DefaultStr }}>{{ e.Value }}{% if e.Help %} – {{ e.Help.split("\n")[0] }}{% endif %}</option>{% endfor %}</select>
{% elif q.Examples %}<input type="text" name="result" list="wz" value="{{ q.DefaultStr }}"><datalist id="wz">{% for e in q.Examples %}<option value="{{ e.Value }}">{{ e.Help.split("\n")[0] if e.Help }}</option>{% endfor %}</datalist>
{% else %}<input type="{{ 'password' if q.IsPassword else 'text' }}" name="result" value="{{ q.DefaultStr }}">{% endif %}
{% endif %}
<p style="margin-top:16px"><button class="btn pri">Weiter</button>
<a class="btn" href="/remotes">Später fortsetzen</a></p>
</form></div>
{% endblock %}""",
"tpl_editor.html": r"""{# erwartet: items (msgtpl.editor_data), prefix #}
{% for ev, t in items.items() %}<details class="tpl" data-ev="{{ ev }}" data-prefix="{{ prefix }}">
<summary><b>{{ t.label }}</b> <span class="tag {{ 'ok' if t.custom else '' }} tplstate">{{ "eigener Text" if t.custom else "Standard" }}</span></summary>
<div class="tplbody">
<label>Betreff</label><input type="text" name="{{ prefix }}{{ ev }}_title" value="{{ t.title }}" class="tt">
<label>Text</label><textarea name="{{ prefix }}{{ ev }}_body" rows="5" class="tb" spellcheck="false">{{ t.body }}</textarea>
<div class="hint" style="margin:6px 0 4px">Variablen (anklicken fügt sie an der Cursor-Position ein):</div>
<div class="chips vars">{% for n, d in t.vars %}<button type="button" class="chip" data-v="{{ n }}" title="{{ d }}">{{ "{" ~ n ~ "}" }}</button>{% endfor %}</div>
<label style="margin-top:10px">Vorschau mit Beispieldaten</label>
<div class="preview"><div class="pt"></div><pre class="pb"></pre></div>
<p style="margin:8px 0 0"><button type="button" class="btn sm reset">↺ Auf Standard zurücksetzen</button></p>
</div></details>{% endfor %}
<script>
(function(){const D={{ items|tojson }};
{% raw %}const R=(txt,v)=>String(txt||'').replace(/\{\{|\}\}|\{([a-z_]+)\}/g,(m,n)=>m==='{{'?'{':m==='}}'?'}':(n in v?String(v[n]??''):m));{% endraw %}
document.querySelectorAll('details.tpl[data-prefix="{{ prefix }}"]').forEach(box=>{const ev=box.dataset.ev,d=D[ev];
  const tt=box.querySelector('.tt'),tb=box.querySelector('.tb');let last=tb;
  [tt,tb].forEach(el=>el.addEventListener('focus',()=>last=el));
  const upd=()=>{const v=Object.assign({},d.sample);const ti=R(tt.value,v).trim();v.titel=ti;
    box.querySelector('.pt').textContent=ti;box.querySelector('.pb').textContent=R(tb.value,v).trim();
    const own=tt.value.trim()!==d.default.title.trim()||tb.value.trim()!==d.default.body.trim();
    const st=box.querySelector('.tplstate');st.textContent=own?'eigener Text':'Standard';st.classList.toggle('ok',own)};
  [tt,tb].forEach(el=>el.addEventListener('input',upd));
  box.querySelectorAll('.vars .chip').forEach(c=>c.addEventListener('click',()=>{const ins='{'+c.dataset.v+'}';
    const a=last.selectionStart??last.value.length,b=last.selectionEnd??a;last.value=last.value.slice(0,a)+ins+last.value.slice(b);
    last.focus();last.selectionStart=last.selectionEnd=a+ins.length;upd()}));
  box.querySelector('.reset').addEventListener('click',()=>{tt.value=d.default.title;tb.value=d.default.body;upd()});
  upd()})})();
</script>""",
"settings.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}{% block body %}{% include "tabs.html" %}<p class="mut" style="margin:-6px 0 14px">Standard-Benachrichtigungen für alle Aufgaben. Jede Aufgabe kann eigene festlegen.</p>
{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
<form method="post"><fieldset {{ "disabled" if not can("notify.edit") }}>
<div class="card"><h2>Standard</h2>
<label>Wann benachrichtigen</label>
<select name="when"><option value="always" {{ "selected" if s.when == "always" }}>immer (Erfolg und Fehler)</option>
<option value="fail" {{ "selected" if s.when == "fail" }}>nur bei Fehler</option>
<option value="never" {{ "selected" if s.when == "never" }}>nie</option></select>
<div class="hint">Gilt für alle Aufgaben mit „Standard verwenden“. In jeder Aufgabe kannst du eigene Kanäle, Empfänger und Zeitpunkte festlegen. Die Nachricht enthält Status, Dauer, Anzahl kopierter und gelöschter Dateien und die letzten Fehler.</div>
</div>

<div class="card" id="quiet"><h2>Ruhezeiten</h2>
<input type="hidden" name="ext_present" value="1">
<label class="check"><input type="checkbox" name="quiet_enabled" id="q_on" {{ "checked" if s.quiet_enabled }} onchange="document.getElementById('qbox').style.display=this.checked?'':'none'"> Ruhezeit für Benachrichtigungen{% if quiet_active %} <span class="tag gestoppt">gerade aktiv</span>{% endif %}</label>
<div id="qbox" style="{{ '' if s.quiet_enabled else 'display:none' }}">
<div class="row" style="margin-top:6px"><div style="flex:0 0 150px"><label>Von</label><input type="time" name="quiet_start" value="{{ s.quiet_start or '22:00' }}"></div>
<div style="flex:0 0 150px"><label>Bis</label><input type="time" name="quiet_end" value="{{ s.quiet_end or '07:00' }}"></div>
<div style="flex:1 1 280px"><label>An diesen Tagen (Beginn)</label><div class="chips" style="margin:4px 0 0">{% for d in range(7) %}<label class="check" style="margin:0 10px 0 0"><input type="checkbox" name="quiet_day_{{ d }}" {{ "checked" if not s.quiet_days or d in s.quiet_days }}> {{ ["Mo","Di","Mi","Do","Fr","Sa","So"][d] }}</label>{% endfor %}</div></div></div>
<label>In der Ruhezeit</label><select name="quiet_mode" style="max-width:520px">
<option value="errors" {{ "selected" if s.quiet_mode != "none" }}>nur Fehler und Warnungen melden, keine Erfolge</option>
<option value="none" {{ "selected" if s.quiet_mode == "none" }}>gar nichts melden</option></select>
<div class="hint">Unterdrückt werden Erfolgsmeldungen, Sicherungen und Update-Hinweise. Fehler, Löschwarnungen, wenig Speicher und gesperrte Anmeldungen kommen im ersten Fall trotzdem. Geht die Zeit über Mitternacht (z. B. 22:00 bis 07:00), zählt der Wochentag des Beginns. Testnachrichten und der Wochenbericht kommen immer.</div>
</div></div>

<div class="card" id="report"><h2>Wochenbericht</h2>
<label class="check"><input type="checkbox" name="report_enabled" id="r_on" {{ "checked" if s.report_enabled }} onchange="document.getElementById('rbox').style.display=this.checked?'':'none'"> Regelmäßig einen Bericht senden</label>
<div id="rbox" style="{{ '' if s.report_enabled else 'display:none' }}">
<div class="row" style="margin-top:6px"><div style="flex:1 1 280px"><label>An diesen Tagen</label><div class="chips" style="margin:4px 0 0">{% for d in range(7) %}<label class="check" style="margin:0 10px 0 0"><input type="checkbox" name="report_day_{{ d }}" {{ "checked" if d in (s.report_days or [0]) }}> {{ ["Mo","Di","Mi","Do","Fr","Sa","So"][d] }}</label>{% endfor %}</div></div>
<div style="flex:0 0 150px"><label>Uhrzeit</label><input type="time" name="report_time" value="{{ s.report_time or '08:00' }}"></div>
<div style="flex:0 0 200px"><label>Zeitraum (Tage)</label><input type="text" inputmode="numeric" name="report_period" value="{{ s.report_period or '7' }}"></div></div>
<label>Über diese Kanäle</label><div class="chips" style="margin:4px 0 0">{% for c, n in [("webhook","Webhook"),("smtp","E-Mail"),("telegram","Telegram"),("apprise","Apprise")] %}<label class="check" style="margin:0 12px 0 0"><input type="checkbox" name="report_ch_{{ c }}" {{ "checked" if c in (s.report_channels or []) }}> {{ n }}</label>{% endfor %}</div>
<div class="hint">Keiner ausgewählt = alle aktiven Kanäle. Der Bericht nennt je Aufgabe Läufe, Erfolge, Fehler und übertragene Daten, dazu die Fehler im Zeitraum, offene Löschwarnungen, Prüfläufe, knappen Speicher und das Datenvolumen. Den Text passt du oben unter „Wochenbericht“ an, ein Webhook bekommt die Zahlen zusätzlich als <code>report</code>.{% if next_report %} Nächster Bericht: {{ next_report }}.{% endif %}</div>
</div>
{% if report_last %}<p class="hint">Zuletzt gesendet: {{ report_last.at|dt }}{% if report_last.results %} ({% for k, v in report_last.results.items() %}{{ k }} {{ "✓" if v is none else "✗" }}{{ ", " if not loop.last }}{% endfor %}){% endif %}</p>{% endif %}
{% if can("notify.edit") %}<p><button class="btn sm" type="submit" form="reportform">{{ ICON.bell }} Bericht jetzt senden</button></p>{% endif %}
</div>

<div class="card"><h2>Texte der Benachrichtigungen</h2>
<p class="mut" style="margin-top:-4px">Betreff und Text je Ereignis mit Variablen anpassen. Gilt für alle Kanäle (E-Mail-Betreff, Telegram, Apprise, Webhook). Ohne Änderung wird der Standardtext verwendet. Jede Aufgabe kann für ihre Läufe eigene Texte haben.</p>
<input type="hidden" name="tpl_present" value="1">
{% with items=tpl_data, prefix="tpl_" %}{% include "tpl_editor.html" %}{% endwith %}
<div class="hint">Unbekannte Variablen bleiben unverändert stehen. Für geschweifte Klammern im Text <code>{{ "{{" }}</code> und <code>{{ "}}" }}</code> schreiben.</div>
</div>

<div class="card"><h3>Webhook</h3>
<label class="check"><input type="checkbox" name="webhook_enabled" {{ "checked" if s.webhook_enabled }}> aktiv</label>
<div class="row"><div style="flex:4"><label>URL</label><input type="text" name="webhook_url" value="{{ s.webhook_url }}" placeholder="https://ntfy.sh/mein-thema  oder  Discord-/Slack-/Home-Assistant-/n8n-Webhook"></div>
<div style="flex:1"><label>Methode</label><select name="webhook_method"><option {{ "selected" if s.webhook_method == "POST" }}>POST</option><option {{ "selected" if s.webhook_method == "PUT" }}>PUT</option></select></div></div>
<div class="hint">Standard: JSON mit <code>job, status, ok, duration, source, dest, copied, deleted, errors, title, message</code>. Die Felder <code>text</code> und <code>content</code> enthalten den Nachrichtentext, damit Slack, Mattermost und Discord ihn direkt anzeigen.</div>
<details class="tpl" id="whbox" {{ "open" if s.webhook_body }}><summary><b>Eigener JSON-Body</b> <span class="tag {{ 'ok' if s.webhook_body }}" id="whstate">{{ "eigene Vorlage" if s.webhook_body else "Standard" }}</span></summary><div class="tplbody">
<textarea name="webhook_body" id="whbody" rows="6" spellcheck="false" placeholder='leer = Standard-JSON. Beispiel: {"content": "{nachricht}"}'>{{ s.webhook_body }}</textarea>
<div class="hint" style="margin:6px 0 4px">Variablen in Anführungszeichen setzen, z. B. <code>"text": "{nachricht}"</code>, Zahlen dürfen ohne: <code>"copied": {kopiert}</code>. Werte werden JSON-sicher eingesetzt. Zusätzlich: <code>{titel}</code>, <code>{nachricht}</code>, <code>{ereignis}</code> (run_ok, run_fail, login_fail …), <code>{ok}</code> (true/false).</div>
<div class="chips vars" id="whvars">{% for n in ["titel","nachricht","ereignis","ok","job","status","quelle","ziel","dauer_s","kopiert","geloescht","fehler","start","ende","datum","zeit"] %}<button type="button" class="chip" data-v="{{ n }}">{{ "{" ~ n ~ "}" }}</button>{% endfor %}</div>
<div class="chips" style="margin-top:6px"><span class="hint">Vorlage einfügen:</span>
<button type="button" class="chip" data-ex='{"content": "{nachricht}"}'>Discord</button>
<button type="button" class="chip" data-ex='{"text": "{nachricht}"}'>Slack / Mattermost</button>
<button type="button" class="chip" data-ex='{"title": "{titel}", "message": "{nachricht}", "priority": 5}'>Gotify</button>
<button type="button" class="chip" data-ex='{"event": "{ereignis}", "job": "{job}", "ok": {ok}, "copied": {kopiert}, "deleted": {geloescht}, "errors": {fehler}, "text": "{nachricht}"}'>Home Assistant / n8n</button></div>
<label style="margin-top:10px">Vorschau mit Beispieldaten (Lauf fehlgeschlagen)</label>
<pre class="preview pb" id="whprev"></pre><div class="hint" id="whok"></div>
</div></details>
<script>(function(){const V={{ wh_sample|tojson }};const ta=document.getElementById('whbody');
const J=v=>JSON.stringify(String(v??'')).slice(1,-1);
{% raw %}const R=t=>String(t||'').replace(/\{\{|\}\}|\{([a-z_]+)\}/g,(m,n)=>m==='{{'?'{':m==='}}'?'}':(n in V?J(V[n]):m));{% endraw %}
function upd(){const t=ta.value.trim(),p=document.getElementById('whprev'),ok=document.getElementById('whok'),st=document.getElementById('whstate');
  st.textContent=t?'eigene Vorlage':'Standard';st.classList.toggle('ok',!!t);
  if(!t){p.textContent='(Standard-JSON)';ok.textContent='';return}const out=R(t);
  try{p.textContent=JSON.stringify(JSON.parse(out),null,2);ok.textContent='✓ gültiges JSON';ok.className='hint ok'}
  catch(e){p.textContent=out;ok.textContent='✗ kein gültiges JSON: '+e.message;ok.className='hint fehler'}}
ta.addEventListener('input',upd);
document.querySelectorAll('#whvars .chip').forEach(c=>c.onclick=()=>{const ins='{'+c.dataset.v+'}',a=ta.selectionStart??ta.value.length,b=ta.selectionEnd??a;
  ta.value=ta.value.slice(0,a)+ins+ta.value.slice(b);ta.focus();ta.selectionStart=ta.selectionEnd=a+ins.length;upd()});
document.querySelectorAll('#whbox [data-ex]').forEach(c=>c.onclick=()=>{ta.value=c.dataset.ex;upd()});upd()})();</script>
<p><button class="btn sm" name="test" value="webhook">Speichern und testen</button></p></div>

<div class="card"><h3>E-Mail (SMTP)</h3>
<label class="check"><input type="checkbox" name="smtp_enabled" {{ "checked" if s.smtp_enabled }}> aktiv</label>
<div class="row"><div style="flex:3"><label>SMTP-Server</label><input type="text" name="smtp_host" value="{{ s.smtp_host }}" placeholder="smtp.example.de"></div>
<div><label>Port</label><input type="text" name="smtp_port" value="{{ s.smtp_port }}"></div>
<div style="flex:2"><label>Verschlüsselung</label><select name="smtp_security">
<option value="starttls" {{ "selected" if s.smtp_security == "starttls" }}>STARTTLS (meist Port 587)</option>
<option value="ssl" {{ "selected" if s.smtp_security == "ssl" }}>SSL/TLS (meist Port 465)</option>
<option value="none" {{ "selected" if s.smtp_security == "none" }}>keine (Port 25, nur intern)</option></select></div></div>
<div class="row"><div><label>Benutzer</label><input type="text" name="smtp_user" value="{{ s.smtp_user }}" autocomplete="off"></div>
<div><label>Passwort</label><input type="password" name="smtp_pass" autocomplete="new-password" placeholder="{{ '(gespeichert, leer lassen = unverändert)' if has_secret.smtp_pass }}"></div></div>
<div class="row"><div><label>Absender</label><input type="text" name="smtp_from" value="{{ s.smtp_from }}" placeholder="mirrorsync@example.de (leer = Benutzer)"></div>
<div><label>Empfänger (mehrere mit Komma)</label><input type="text" name="smtp_to" value="{{ s.smtp_to }}" placeholder="admin@example.de"></div></div>
<p><button class="btn sm" name="test" value="smtp">Speichern und testen</button></p></div>

<div class="card"><h3>Telegram</h3>
<label class="check"><input type="checkbox" name="telegram_enabled" {{ "checked" if s.telegram_enabled }}> aktiv</label>
<div class="row"><div style="flex:2"><label>Bot-Token</label><input type="password" name="telegram_token" autocomplete="new-password" placeholder="{{ '(gespeichert, leer lassen = unverändert)' if has_secret.telegram_token else '123456789:AA…' }}"></div>
<div><label>Chat-ID</label><input type="text" name="telegram_chat_id" value="{{ s.telegram_chat_id }}" placeholder="z. B. 12345678 oder -100…"></div></div>
<div class="hint">Bot anlegen: In Telegram <code>@BotFather</code> anschreiben, <code>/newbot</code>, Token hier eintragen. Dann deinem Bot einmal „hallo“ schreiben und
<code>https://api.telegram.org/bot&lt;TOKEN&gt;/getUpdates</code> öffnen, dort steht unter <code>chat → id</code> deine Chat-ID. Für Gruppen den Bot in die Gruppe einladen.</div>
<p><button class="btn sm" name="test" value="telegram">Speichern und testen</button></p></div>

<div class="card"><h3>Apprise</h3>
<label class="check"><input type="checkbox" name="apprise_enabled" {{ "checked" if s.apprise_enabled }}> aktiv</label>
<p class="mut" style="margin-top:0">Ein Kanal für über 100 Dienste: Discord, ntfy, Pushover, Gotify, Signal, Matrix, Teams, Slack, Home Assistant, E-Mail und mehr.</p>
<label>Senden</label>
<div class="seg" id="apmode">
<label><input type="radio" name="apprise_mode" value="lib" {{ "checked" if s.apprise_mode != "api" }} onchange="apShow()"><span>Direkt aus MirrorSync</span></label>
<label><input type="radio" name="apprise_mode" value="api" {{ "checked" if s.apprise_mode == "api" }} onchange="apShow()"><span>Über einen Apprise-API-Server</span></label></div>
<div class="ap-api"><div class="row"><div style="flex:2"><label>Adresse des Apprise-API-Servers</label><input type="text" name="apprise_api_url" value="{{ s.apprise_api_url }}" placeholder="http://192.168.1.20:8000"></div>
<div><label>Konfigurations-Key (optional)</label><input type="password" name="apprise_api_key" autocomplete="new-password" placeholder="{{ '(gespeichert, leer lassen = unverändert)' if has_secret.apprise_api_key else 'z. B. mirrorsync' }}"></div></div>
{% if has_secret.apprise_api_key %}<label class="check"><input type="checkbox" name="apprise_api_key_clear"> Key entfernen</label>{% endif %}
<div class="hint">Mit Key werden die Ziele genutzt, die auf dem Server unter diesem Key gespeichert sind (<code>/notify/&lt;key&gt;</code>), der Tag wählt welche. Ohne Key schickt MirrorSync die URLs unten mit (<code>/notify</code>).</div></div>
<label>Apprise-URLs (eine pro Zeile)</label>
<textarea name="apprise_urls" rows="4" autocomplete="off" spellcheck="false" placeholder="{{ ('Gespeichert: ' ~ ap_saved|join(', ') ~ '  (leer lassen = unverändert, neue Eingabe ersetzt alle)') if ap_saved else 'ntfy://ntfy.sh/mein-thema&#10;discord://webhook_id/webhook_token&#10;pover://user_key@app_token' }}"></textarea>
{% if ap_saved %}<label class="check"><input type="checkbox" name="apprise_urls_clear"> gespeicherte URLs entfernen</label>{% endif %}
<div class="row"><div><label>Tag (optional)</label><input type="text" name="apprise_tag" value="{{ s.apprise_tag }}" placeholder="z. B. backup"></div><div></div></div>
<div class="hint">Format der URLs siehe <a href="https://github.com/caronc/apprise/wiki" target="_blank" rel="noopener">Apprise-Wiki</a>. Die URLs enthalten Zugangsdaten, daher werden sie nach dem Speichern nicht mehr angezeigt und nie ins Audit-Log geschrieben.{% if not ap_lib %} <span class="fehler">Die Apprise-Bibliothek fehlt in diesem Image, „Direkt“ geht erst nach einem Neubau.</span>{% endif %}</div>
<p><button class="btn sm" name="test" value="apprise">Speichern und testen</button></p></div>
<script>function apShow(){const api=document.querySelector('[name=apprise_mode]:checked').value==='api';document.querySelector('.ap-api').style.display=api?'':'none'}apShow()</script>

<p><button class="btn pri">Speichern</button> {% if can("notify.edit") %}<button class="btn" type="submit" form="testallform" title="Schickt eine Probe-Nachricht an alle aktiven Kanäle (gespeicherte Einstellungen)">{{ ICON.bell }} Probe an alle Kanäle</button>{% endif %}</p>
<p class="hint">Zugangsdaten werden in <code>config/settings.json</code> gespeichert (nur für den Container lesbar). „Probe an alle Kanäle“ nutzt die gespeicherten Einstellungen, vorher also speichern.</p>
</fieldset></form>
<form id="testallform" method="post" action="/settings/notify/test-all"></form>
<form id="reportform" method="post" action="/settings/report/send"></form>
{% endblock %}""",
"login.html": r"""<!doctype html>
<html lang="{{ lang_code() }}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anmelden · MirrorSync</title><link rel="icon" href="/static/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/static/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#4f46e5">
<script>try{const t=localStorage.getItem('ms-theme');if(t)document.documentElement.dataset.theme=t}catch(e){}</script>
<style>
:root{--bg:#f6f7f9;--card:#fff;--card2:#f9fafb;--fg:#0f172a;--mut:#64748b;--bd:#e5e7eb;--bd2:#d1d5db;--acc:#4f46e5;--acc-fg:#fff;--acc-soft:rgba(79,70,229,.12);--err:#dc2626;--err-soft:rgba(220,38,38,.1)}
:root[data-theme=dark]{--bg:#09090b;--card:#111114;--card2:#16161a;--fg:#ececf1;--mut:#8b8b98;--bd:#232329;--bd2:#2e2e36;--acc:#8b93ff;--acc-fg:#0b0b10;--acc-soft:rgba(139,147,255,.16);--err:#f87171;--err-soft:rgba(248,113,113,.12)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#09090b;--card:#111114;--card2:#16161a;--fg:#ececf1;--mut:#8b8b98;--bd:#232329;--bd2:#2e2e36;--acc:#8b93ff;--acc-fg:#0b0b10;--acc-soft:rgba(139,147,255,.16);--err:#f87171;--err-soft:rgba(248,113,113,.12)}}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:16px;font:14px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Inter,sans-serif;background:var(--bg);color:var(--fg);
background-image:radial-gradient(600px 300px at 50% 0%,var(--acc-soft),transparent)}
.box{width:100%;max-width:380px;background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:28px}
.brand{display:flex;align-items:center;gap:10px;font-weight:650;font-size:17px;margin-bottom:6px}
.logo{width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,var(--acc),#a855f7);display:grid;place-items:center;color:#fff}
.logo svg{width:18px;height:18px}p.sub{color:var(--mut);margin:0 0 18px}
label{display:block;margin:12px 0 5px;font-weight:550;font-size:13.5px}
input[type=text],input[type=password]{width:100%;height:38px;padding:0 11px;border:1px solid var(--bd2);border-radius:8px;background:var(--card2);color:var(--fg);font:inherit;outline:none}
input:focus{border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}
.check{display:flex;gap:8px;align-items:center;margin:14px 0 18px;color:var(--mut)}.check input{accent-color:var(--acc)}
button{width:100%;height:40px;border:0;border-radius:8px;background:var(--acc);color:var(--acc-fg);font:inherit;font-weight:600;cursor:pointer}button:hover{filter:brightness(1.08)}
.err{padding:10px 12px;border-radius:8px;border:1px solid var(--err);background:var(--err-soft);margin-bottom:6px}
.ver{text-align:center;color:var(--mut);font-size:12px;margin-top:16px}
button.alt{background:var(--card2);color:var(--fg);border:1px solid var(--bd2)}
.or{display:flex;align-items:center;gap:10px;color:var(--mut);font-size:12px;margin:14px 0}.or::before,.or::after{content:"";flex:1;height:1px;background:var(--bd)}
code{font-family:ui-monospace,monospace;font-size:12px;background:var(--card2);border:1px solid var(--bd);border-radius:5px;padding:0 4px}
</style></head><body>
<form class="box" method="post">
<div class="brand"><div class="logo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5"/><path d="M3 21v-5h5"/></svg></div>MirrorSync</div>
{% if mode == "login" %}<div style="display:flex;justify-content:flex-end;margin:-34px 0 14px"><select aria-label="Language" onchange="location.href=location.pathname+'?lang='+this.value" style="height:28px;border:1px solid var(--bd2);border-radius:7px;background:var(--card2);color:var(--fg);font:inherit;font-size:12.5px;padding:0 6px">{% for c, n in LANGS() %}<option value="{{ c }}" {{ "selected" if c == lang_code() }}>{{ n }}</option>{% endfor %}</select></div>{% endif %}
{% if mode == "setup" %}<p class="sub">Willkommen! Schritt 1 von 2: Lege den ersten Admin-Benutzer an.</p>
<label for="lng">Sprache</label><select id="lng" name="language" onchange="location.href=location.pathname+'?lang='+this.value" style="width:100%;height:38px;padding:0 8px;border:1px solid var(--bd2);border-radius:8px;background:var(--card2);color:var(--fg);font:inherit">{% for c, n in LANGS() %}<option value="{{ c }}" {{ "selected" if c == lang_code() }}>{{ n }}</option>{% endfor %}</select>
<p class="sub" style="margin:6px 0 0;font-size:12.5px">Standard für neue Benutzer, die Anmeldeseite, Benachrichtigungen und die API. Jeder Benutzer kann seine Sprache unter „Mein Konto“ ändern.</p>
{% elif mode == "2fa" %}<p class="sub">Zwei-Faktor-Anmeldung für <b>{{ user }}</b></p>
{% else %}<p class="sub">Bitte melde dich an.</p>{% endif %}
{% if err %}<div class="err">{{ err }}</div>{% endif %}
{% if mode == "2fa" %}
<label for="c">6-stelliger Code aus der Authenticator-App</label>
<input id="c" type="text" name="code" inputmode="numeric" autocomplete="one-time-code" autofocus required placeholder="123456" style="letter-spacing:.3em;font-size:18px;text-align:center">
<p class="sub" style="margin:10px 0 16px;font-size:12.5px">Kein Handy zur Hand? Gib stattdessen einen deiner Backup-Codes ein.</p>
<button>Bestätigen</button>
<p style="text-align:center;margin:14px 0 0"><a href="/login" style="color:var(--mut);font-size:13px">Abbrechen</a></p>
{% else %}
{% if mode == "setup" and need_token %}<label for="tok">Einrichtungs-Code</label><input id="tok" type="text" name="token" value="{{ token_typed or '' }}" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="XXXX-XXXX-XXXX" required autofocus style="letter-spacing:.12em;font-family:ui-monospace,monospace">
<p class="sub" style="margin:6px 0 0;font-size:12.5px">Steht im Container-Log: <code>docker logs mirrorsync</code> (oder in <code>config/setup_token</code>). Damit kann niemand sonst deinen Container übernehmen, bevor du den Admin angelegt hast.</p>{% endif %}
<label for="u">Benutzername</label><input id="u" type="text" name="user" value="{{ user }}" autocomplete="username" {{ "" if user or (mode == "setup" and need_token) else "autofocus" }} required>
<label for="pw">Passwort</label><input id="pw" type="password" name="password" autocomplete="{{ 'new-password' if mode == 'setup' else 'current-password' }}" {{ "autofocus" if user and mode != "setup" }} required>
{% if mode == "setup" %}<label for="pw2">Passwort wiederholen</label><input id="pw2" type="password" name="password2" autocomplete="new-password" required>
<p class="sub" style="margin:8px 0 16px;font-size:12.5px">Mindestens 8 Zeichen. Im nächsten Schritt kannst du optional 2FA und einen Passkey einrichten.</p>
<button>Admin anlegen</button>
{% else %}<label class="check"><input type="checkbox" name="remember" checked> Angemeldet bleiben (30 Tage)</label>
<button>Anmelden</button>
<div id="pkbox" style="display:none"><div class="or"><span>oder</span></div>
<button type="button" class="alt" id="pkbtn" onclick="pkLogin()"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-3px;margin-right:6px"><circle cx="8" cy="15" r="4"/><path d="M10.85 12.15 19 4"/><path d="m18 5 2 2"/><path d="m15 8 2 2"/></svg>Mit Passkey anmelden</button>
<div id="pkmsg" class="sub" style="margin:8px 0 0;font-size:12.5px"></div></div>
<script>
{% raw %}const b64u={dec:s=>Uint8Array.from(atob(s.replace(/-/g,'+').replace(/_/g,'/')+'==='.slice((s.length+3)%4)),c=>c.charCodeAt(0)).buffer,
 enc:b=>btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')};
function pkCredJSON(c){if(c.toJSON)try{return c.toJSON()}catch(e){}const r=c.response,o={id:c.id,rawId:b64u.enc(c.rawId),type:c.type,clientExtensionResults:c.getClientExtensionResults?c.getClientExtensionResults():{},response:{clientDataJSON:b64u.enc(r.clientDataJSON)}};
 if(r.authenticatorData)o.response.authenticatorData=b64u.enc(r.authenticatorData);if(r.signature)o.response.signature=b64u.enc(r.signature);if(r.userHandle)o.response.userHandle=b64u.enc(r.userHandle);
 if(r.attestationObject)o.response.attestationObject=b64u.enc(r.attestationObject);if(r.getTransports)o.response.transports=r.getTransports();if(c.authenticatorAttachment)o.authenticatorAttachment=c.authenticatorAttachment;return o}
async function pkLogin(){const m=document.getElementById('pkmsg');m.textContent='Warte auf den Passkey …';m.style.color='';
 try{let r=await fetch('/login/passkey/options',{method:'POST',headers:{Accept:'application/json'}});let o=await r.json();if(o.ok===false)throw new Error(o.error);
  o.challenge=b64u.dec(o.challenge);(o.allowCredentials||[]).forEach(c=>c.id=b64u.dec(c.id));
  const cred=await navigator.credentials.get({publicKey:o});
  const rem=document.querySelector('[name=remember]');
  r=await fetch('/login/passkey',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({credential:pkCredJSON(cred),remember:rem&&rem.checked})});
  const res=await r.json();if(!res.ok)throw new Error(res.error);location.href=res.next||'/'}
 catch(e){m.style.color='var(--err)';m.textContent=e.name==='NotAllowedError'?'Abgebrochen oder kein passender Passkey auf diesem Gerät.':(e.message||String(e))}}
if({% endraw %}{{ "false" if pk_off else "true" }}{% raw %}&&window.PublicKeyCredential&&window.isSecureContext)document.getElementById('pkbox').style.display='';{% endraw %}
</script>
{% if pk_hint %}<p class="sub" style="margin:12px 0 0;font-size:12px">{{ pk_hint }}</p>{% endif %}
{% endif %}
{% endif %}
<div class="ver">v{{ VERSION }}</div>
</form>
</body></html>
""",
"tabs.html": r"""<div class="tabs">{% if can('users.view') %}<a href="/users" class="{{ 'active' if request.path.startswith('/users') }}">Benutzer{% if fail_badge %}<span class="badge">{{ fail_badge }}</span>{% endif %}</a>{% endif %}
{% if can('roles.manage') %}<a href="/roles" class="{{ 'active' if request.path.startswith('/roles') }}">Rollen</a>{% endif %}
{% if can('groups.manage') %}<a href="/groups" class="{{ 'active' if request.path.startswith('/groups') }}">Gruppen</a>{% endif %}
{% if can('notify.view') %}<a href="/settings" class="{{ 'active' if request.path == '/settings' }}">Benachrichtigungen</a>{% endif %}
{% if can('system.settings') %}<a href="/settings/general" class="{{ 'active' if request.path.startswith('/settings/general') }}">Allgemein</a>{% endif %}
{% if can('system.access') %}<a href="/settings/access" class="{{ 'active' if request.path.startswith('/settings/access') }}">Zugriff</a>{% endif %}
{% if can('system.api') %}<a href="/settings/api" class="{{ 'active' if request.path.startswith('/settings/api') }}">API</a>{% endif %}
{% if g.role == 'admin' %}<a href="/settings/backup" class="{{ 'active' if request.path.startswith('/settings/backup') }}">Sicherung</a>{% endif %}
<a href="/account" class="{{ 'active' if request.path.startswith('/account') }}">Mein Konto</a>
<a href="/help{{ HELP_ANCHOR.get(request.path, '') }}" class="helptab{{ ' active' if request.path.startswith('/help') }}" style="margin-left:auto" title="Hilfe: alle Einstellungen erklärt, mit Suche">❓ Hilfe</a></div>
""",
"backup.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}
{% block body %}{% include "tabs.html" %}
{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
{% if preview %}{% set m = preview.m %}
<div class="card" style="border-color:{{ 'var(--acc)' if preview.ok else 'var(--err)' }}"><h2>Import prüfen: {{ preview.name }}</h2>
<table><tr><th>Exportiert</th><td>{{ m.created }}{% if m.note %} · {{ m.note }}{% endif %}{% if preview.enc %} · verschlüsselt{% endif %}</td></tr>
<tr><th>Version</th><td>MirrorSync {{ m.version }} (Datenformat {{ m.schema }}) · hier läuft {{ VERSION }}</td></tr></table>
{% for n in preview.notes %}<div class="msg {{ 'info' if preview.ok else 'err' }}" style="margin:10px 0 0">{{ n }}</div>{% endfor %}
<h3>Inhalt</h3><table><tr><th>Bereich</th><th class="num">in der Datei</th><th class="num">jetzt</th></tr>
{% for k, label in labels.items() %}<tr><td>{{ label }}</td><td class="num"><b>{{ preview.counts.get(k, 0) }}</b></td><td class="num mut">{{ counts.get(k, 0) }}</td></tr>{% endfor %}
<tr><td>Dateien (rclone.conf, Schlüssel …)</td><td class="num"><b>{{ preview.files|length }}</b></td><td class="num mut">{{ files|length }}</td></tr>
{% if preview.logs %}<tr><td>Lauf-Logs</td><td class="num"><b>{{ preview.logs }}</b></td><td></td></tr>{% endif %}</table>
{% if preview.files %}<p class="hint">Dateien: {% for f in preview.files %}<code>{{ f }}</code> {% endfor %}</p>{% endif %}
{% if preview.ok %}<form method="post" action="/settings/backup/apply" style="margin-top:14px">
<label class="check"><input type="checkbox" name="files" checked> rclone.conf, SSH-Schlüssel und andere Dateien übernehmen (gleichnamige Dateien werden überschrieben)</label>
{% if preview.logs %}<label class="check"><input type="checkbox" name="logs"> Lauf-Logs übernehmen</label>{% endif %}
<label class="check"><input type="checkbox" name="confirm" required> <span>Ich will den aktuellen Stand <b>komplett ersetzen</b> (Aufgaben, Benutzer, Rollen, Einstellungen, Logs). Vorher wird automatisch eine Sicherung angelegt.</span></label>
<p><button class="btn pri">Jetzt ersetzen</button> <button class="btn" name="cancel" value="1" formnovalidate>Abbrechen</button></p></form>
{% else %}<form method="post" action="/settings/backup/apply"><p><button class="btn" name="cancel" value="1">Verwerfen</button></p></form>{% endif %}
</div>{% endif %}

<div class="card"><h2>Exportieren</h2>
<p class="mut" style="margin-top:0">Lädt den gesamten Stand als ZIP herunter: Aufgaben mit Verlauf, Zeitpläne, Speicherorte (rclone.conf), SSH-Schlüssel, Benutzer, Rollen, Einstellungen, Vorlagen, IP-Regeln, Anmeldeverlauf und Audit-Log.</p>
<div class="msg err" style="margin:0 0 12px">⚠️ <b>Die Datei enthält Geheimnisse:</b> Zugangsdaten aller Speicherorte, Passwort-Hashes, 2FA-Schlüssel, Passkeys, Tokens und Webhook-Adressen. Wer sie hat, kann sich Zugang zu deinen Servern verschaffen. Am besten mit Passwort verschlüsseln und sicher aufbewahren.</div>
<form method="post" action="/settings/backup/export">
<div class="row"><div><label>Passwort für die Verschlüsselung (empfohlen)</label><input type="password" name="password" autocomplete="new-password" {{ "disabled" if not crypto }} placeholder="leer = unverschlüsselt"></div>
<div><label>Passwort wiederholen</label><input type="password" name="password2" autocomplete="new-password" {{ "disabled" if not crypto }}></div></div>
<div class="hint">AES-256-GCM, Schlüssel per scrypt aus dem Passwort. Ohne das Passwort lässt sich die Datei nicht mehr öffnen, es gibt keine Wiederherstellung.</div>
<label class="check"><input type="checkbox" name="logs"> Lauf-Logs mitnehmen (kann groß werden)</label>
<p style="margin-top:12px"><button class="btn pri">Exportieren</button></p></form></div>

<div class="card"><h2>Importieren</h2>
<p class="mut" style="margin-top:0">Exportdatei auswählen. Sie wird zuerst geprüft und angezeigt, ersetzt wird erst nach deiner Bestätigung. Vorher legt MirrorSync automatisch eine Sicherung des aktuellen Stands an.</p>
<form method="post" action="/settings/backup/import" enctype="multipart/form-data">
<div class="row"><div><label>Exportdatei (.zip oder .zip.enc)</label><input type="file" name="file" accept=".zip,.enc" required></div>
<div><label>Passwort (nur bei verschlüsselten Dateien)</label><input type="password" name="password" autocomplete="off"></div></div>
<p style="margin-top:12px"><button class="btn">Datei prüfen</button></p></form></div>

<form method="post" action="/settings/backup/auto" class="card"><h2>Automatische Sicherung</h2>
<p class="mut" style="margin-top:0">Sichert den gesamten Stand (wie der Export) nach Zeitplan. Hat sich seit der letzten Sicherung nichts geändert, wird keine neue Datei angelegt. Verlauf, Anmeldungen und Zähler zählen dabei nicht als Änderung.</p>
{% set st = ab.status %}{% if st.result %}<div class="msg {{ 'err' if st.result == 'fail' else 'info' }}" style="margin:0 0 12px">Letzter Lauf {{ st.time }} ({{ st.by }}):
{% if st.result == 'ok' %}Sicherung <code>{{ st.file.split('/')[-1] }}</code> erstellt.{% elif st.result == 'skip' %}nichts geändert, keine neue Sicherung.{% else %}fehlgeschlagen: {{ st.error }}{% endif %}</div>{% endif %}
<label class="check"><input type="checkbox" name="autobackup_enabled" {{ "checked" if ab.autobackup_enabled }}> Automatische Sicherung einschalten</label>
<div class="row"><div><label>Zeitplan (Cron)</label><input type="text" name="autobackup_schedule" value="{{ ab.autobackup_schedule }}" list="ab_presets" required>
<datalist id="ab_presets">{% for c, l in cron_presets %}<option value="{{ c }}">{{ l }}</option>{% endfor %}</datalist>
<div class="hint">{% for c, l in cron_presets %}<a href="#" class="chip" onclick="this.closest('form').autobackup_schedule.value='{{ c }}';return false">{{ l }}</a> {% endfor %}{% if ab.next %}<br>Nächste Sicherung: {{ ab.next }}{% endif %}</div></div>
<div><label>Zielordner im Container</label><input type="text" name="autobackup_dir" value="{{ ab.autobackup_dir }}" placeholder="{{ ab.default_dir }}">
<div class="hint">Leer = <code>{{ ab.default_dir }}</code>. Für eine Kopie außerhalb von config z. B. <code>/backups</code> als Volume einbinden.</div></div></div>
<div class="row"><div><label>Behalten: Anzahl Sicherungen</label><input type="number" name="autobackup_keep" min="0" value="{{ ab.autobackup_keep }}"></div>
<div><label>Behalten: höchstens Tage</label><input type="number" name="autobackup_days" min="0" value="{{ ab.autobackup_days }}"></div></div>
<div class="hint">0 = keine Grenze. Gilt nur für automatische Sicherungen, die neueste bleibt immer erhalten.</div>
<div class="row"><div><label>Passwort für die Verschlüsselung{% if ab.has_password %} (gesetzt, leer lassen = beibehalten){% endif %}</label><input type="password" name="autobackup_password" autocomplete="new-password" {{ "disabled" if not crypto }} placeholder="{{ '••••••••' if ab.has_password else 'leer = unverschlüsselt' }}"></div>
<div><label>Passwort wiederholen</label><input type="password" name="autobackup_password2" autocomplete="new-password" {{ "disabled" if not crypto }}></div></div>
{% if ab.has_password %}<label class="check"><input type="checkbox" name="autobackup_password_clear"> Passwort entfernen (künftige Sicherungen unverschlüsselt)</label>{% endif %}
<label class="check"><input type="checkbox" name="autobackup_logs" {{ "checked" if ab.autobackup_logs }}> Lauf-Logs mitsichern (kann groß werden, Logs allein lösen keine neue Sicherung aus)</label>
<h3>Benachrichtigung</h3>
<div class="row"><div><label>Melden</label><select name="autobackup_notify">
{% for v, l in [("never", "nie"), ("fail", "nur bei Fehler"), ("always", "bei Erfolg und Fehler")] %}<option value="{{ v }}" {{ "selected" if ab.autobackup_notify == v }}>{{ l }}</option>{% endfor %}</select></div>
<div><label>Kanäle</label><div style="display:flex;gap:14px;flex-wrap:wrap;padding-top:6px">{% for c, n, on in ab.channels %}<label class="check" style="margin:0"><input type="checkbox" name="autobackup_ch_{{ c }}" {{ "checked" if c in (ab.autobackup_channels or []) }}> {{ n }}{% if not on %} <small class="mut">(global aus)</small>{% endif %}</label>{% endfor %}</div>
<div class="hint">Keiner angehakt = alle unter Benachrichtigungen eingeschalteten Kanäle.</div></div></div>
<label class="check"><input type="checkbox" name="autobackup_notify_skip" {{ "checked" if ab.autobackup_notify_skip }}> Auch melden, wenn sich nichts geändert hat (nur bei „bei Erfolg und Fehler“)</label>
<div class="hint">Betreff und Text lassen sich unter Benachrichtigungen → Vorlagen anpassen.</div>
<p style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;align-items:center"><button class="btn pri">Speichern</button>
<button class="btn" name="run" value="1" formnovalidate>Jetzt sichern</button>
<label class="check" style="margin:0"><input type="checkbox" name="force"> auch ohne Änderung</label></p></form>

<div class="card"><h2>Gespeicherte Sicherungen</h2>
{% if backups %}<table><tr><th>Datei</th><th class="hide-sm">Zeit</th><th class="num hide-sm">Größe</th><th style="text-align:right">Aktionen</th></tr>
{% for b in backups %}<tr><td><code>{{ b.name }}</code><br><small class="mut">{{ "automatisch" if b.auto else "vor Import" }}{% if b.enc %} · verschlüsselt{% endif %} · {{ b.dir }}</small></td><td class="hide-sm"><small>{{ b.time }}</small></td><td class="num hide-sm"><small>{{ (b.size / 1024)|round(0)|int }} KB</small></td>
<td style="text-align:right;white-space:nowrap"><a class="btn sm" href="/settings/backup/file/{{ b.name }}">Herunterladen</a>
<form class="inline" method="post" action="/settings/backup/file/{{ b.name }}/restore"><button class="btn sm">Wiederherstellen…</button></form>
<form class="inline" method="post" action="/settings/backup/file/{{ b.name }}/delete" onsubmit="return confirm('Sicherung löschen?')"><button class="btn sm del">Entfernen</button></form></td></tr>{% endfor %}</table>
<p class="hint">„Wiederherstellen…“ prüft die Datei zuerst und zeigt sie oben an, ersetzt wird erst nach Bestätigung. Verschlüsselte automatische Sicherungen werden mit dem gespeicherten Passwort geöffnet. Vor einem Import angelegte Sicherungen liegen unverschlüsselt in <code>config/backups/</code> (nur für root lesbar), die letzten 10 bleiben.</p>
{% else %}<p class="mut" style="margin:0">Noch keine. Vor jedem Import und nach Zeitplan wird hier automatisch eine angelegt.</p>{% endif %}</div>

<div class="card"><h2>Datenbank</h2>
<p class="mut" style="margin:0">SQLite-Datei <code>{{ db_info.path }}</code> · {{ (db_info.size / 1024)|round(0)|int }} KB{% if db_info.migrated %} · eingerichtet {{ db_info.migrated }}{% if db_info["from"] and db_info["from"] != "-" %}, übernommen aus {{ db_info["from"] }} (alte Dateien in <code>config/json-backup/</code>){% endif %}{% endif %}.</p>
<p class="hint">Inhalt: {% for k, label in labels.items() %}{{ label }} {{ counts.get(k, 0) }}{{ " · " if not loop.last }}{% endfor %}.</p></div>
{% endblock %}
""",
"api_keys.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}
{% block body %}{% include "tabs.html" %}
{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
{% if new %}<div class="card" style="border-color:var(--acc)"><h2>API-Key „{{ new.name }}“ erstellt</h2>
<p class="mut" style="margin-top:0"><b style="color:var(--fg)">Jetzt kopieren.</b> Später kannst du ihn in der Liste mit „Anzeigen“ noch einmal sehen, nach Bestätigung mit Passwort (und 2FA-Code) oder Passkey. Gespeichert ist er verschlüsselt.</p>
<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center"><code id="newkey" style="user-select:all;word-break:break-all;font-size:13px;padding:8px 10px;flex:1">{{ new.token }}</code>
<button type="button" class="btn" onclick="navigator.clipboard.writeText(document.getElementById('newkey').textContent);this.textContent='Kopiert'">Kopieren</button></div>
<p class="hint">Test: <code>curl -H "Authorization: Bearer {{ new.token[:16] }}…" {{ base }}/api/v1/status</code></p></div>{% endif %}

<div class="card"><h2>API und MCP</h2>
<p class="mut" style="margin-top:0">Mit einem API-Key steuern n8n, Home Assistant, Skripte oder KI-Assistenten (MCP) MirrorSync. Jeder Key hat eine Rolle und damit genau deren Rechte und Beschränkungen auf Aufgaben und Speicherorte. Es gelten dieselben IP-Sperren wie in der GUI, höchstens 300 Anfragen pro Minute.</p>
<table><tr><th>REST-API</th><td><code>{{ base }}/api/v1</code> · <a href="/api/docs" target="_blank" rel="noopener">Swagger-Dokumentation</a> · <a href="/api/v1/openapi.json" target="_blank" rel="noopener">openapi.json</a></td></tr>
<tr><th>MCP-Server</th><td><code>{{ base }}/mcp</code> (Streamable HTTP, Header <code>Authorization: Bearer &lt;Key&gt;</code>)</td></tr></table></div>

<div class="card"><h2>API-Keys</h2>
{% if rows %}<table><tr><th>Name</th><th>Rolle</th><th class="hide-sm">Gültig bis / IP</th><th class="hide-sm">Zuletzt benutzt</th><th style="text-align:right">Aktionen</th></tr>
{% for k in rows %}<tr style="{{ 'opacity:.55' if k.status != 'aktiv' }}"><td><b>{{ k.name }}</b> {% if k.status == 'aktiv' %}<span class="tag ok">aktiv</span>{% else %}<span class="tag fehler">{{ k.status }}</span>{% endif %}<br><small class="mut"><code>msk_{{ k.id }}_…</code> · erstellt {{ k.created }} von {{ k.created_by }}</small></td>
<td>{{ k.role_name }}{% if k.group_names %}<br><small class="mut">{{ k.group_names|join(", ") }}</small>{% endif %}</td><td class="hide-sm"><small>{{ k.expires or "unbegrenzt" }}{% if k.disabled %}<br>deaktiviert{% endif %}{% if k.lock_from or k.lock_until %}<br>pausiert {{ k.lock_from|dt if k.lock_from else "ab sofort" }} – {{ k.lock_until|dt if k.lock_until else "offen" }}{% endif %}{% if k.windows %}<br>aktiv nur: {{ k.windows_text }}{% endif %}{% if k.ips %}<br>{{ k.ips|join(", ") }}{% else %}<br>alle IPs{% endif %}</small></td>
<td class="hide-sm"><small>{% if k.last_used %}{{ k.last_used }}<br><code>{{ k.last_ip }}</code>{% else %}noch nie{% endif %}</small></td>
<td style="text-align:right;white-space:nowrap"><a class="btn sm" href="/audit?user=API:{{ k.name|urlencode }}">Audit</a>
{% if k.status not in ('widerrufen', 'abgelaufen') and can_reveal.get(k.id) %}{% if k.revealable %}<details class="pausemenu"><summary class="btn sm">Anzeigen</summary><div class="pmenu" style="min-width:290px">
<b>Key anzeigen: bitte bestätigen</b>
<input type="password" class="rv_pw" placeholder="dein Passwort" autocomplete="current-password">
{% if my_totp %}<input type="text" class="rv_code" inputmode="numeric" placeholder="2FA-Code oder Backup-Code" autocomplete="one-time-code">{% endif %}
<button type="button" class="btn sm pri" onclick="rvPw(this,'{{ k.id }}')">Anzeigen</button>
{% if my_pk %}<button type="button" class="btn sm rvpk" onclick="rvPk(this,'{{ k.id }}')" style="display:none">Mit Passkey bestätigen</button>{% endif %}
<div class="hint rv_msg"></div></div></details>
{% else %}<span class="btn sm" style="opacity:.5;cursor:help" title="Vor Version 1.24.0 erstellt: gespeichert ist nur der Hash, der Key lässt sich nicht mehr anzeigen.">nicht anzeigbar</span>{% endif %}{% endif %}
{% if can_reveal.get(k.id) and k.status != 'widerrufen' %}<a class="btn sm" href="/settings/api/{{ k.id }}/edit">Bearbeiten</a>{% endif %}
{% if k.status != 'widerrufen' %}<form class="inline" method="post" action="/settings/api/{{ k.id }}/revoke" onsubmit="return confirm('API-Key {{ k.name }} widerrufen? Programme, die ihn nutzen, verlieren sofort den Zugriff.')"><button class="btn sm del">Widerrufen</button></form>{% endif %}
<form class="inline" method="post" action="/settings/api/{{ k.id }}/delete" data-q="{{ _('API-Key „{0}“ endgültig löschen? Er funktioniert sofort nicht mehr und verschwindet aus der Liste und aus allen Gruppen. Einträge im Audit-Log bleiben.', k.name) }}" onsubmit="return confirm(this.dataset.q)"><button class="btn sm del">Entfernen</button></form></td></tr>{% endfor %}</table>
{% else %}<p class="mut" style="margin:0">Noch keine API-Keys.</p>{% endif %}</div>
<div class="card" id="rvbox" style="display:none;border-color:var(--acc)"><h2 id="rvtitle">API-Key</h2>
<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center"><code id="rvkey" style="user-select:all;word-break:break-all;font-size:13px;padding:8px 10px;flex:1"></code>
<button type="button" class="btn" onclick="navigator.clipboard.writeText(document.getElementById('rvkey').textContent);this.textContent='Kopiert'">Kopieren</button></div>
<p class="hint">Wird nach 60 Sekunden wieder ausgeblendet. Das Anzeigen steht im Audit-Log.</p></div>
<script>
{% raw %}const b64u={dec:s=>Uint8Array.from(atob(s.replace(/-/g,'+').replace(/_/g,'/')+'==='.slice((s.length+3)%4)),c=>c.charCodeAt(0)).buffer,
 enc:b=>btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')};
function pkCredJSON(c){if(c.toJSON)try{return c.toJSON()}catch(e){}const r=c.response,o={id:c.id,rawId:b64u.enc(c.rawId),type:c.type,clientExtensionResults:c.getClientExtensionResults?c.getClientExtensionResults():{},response:{clientDataJSON:b64u.enc(r.clientDataJSON)}};
 if(r.authenticatorData)o.response.authenticatorData=b64u.enc(r.authenticatorData);if(r.signature)o.response.signature=b64u.enc(r.signature);if(r.userHandle)o.response.userHandle=b64u.enc(r.userHandle);return o}
let rvT=null;
function rvShow(btn,tok){const box=document.getElementById('rvbox');document.getElementById('rvkey').textContent=tok;
 document.getElementById('rvtitle').textContent=btn.closest('tr').querySelector('td b').textContent;box.style.display='';box.scrollIntoView({behavior:'smooth'});
 btn.closest('details').removeAttribute('open');clearTimeout(rvT);rvT=setTimeout(()=>{document.getElementById('rvkey').textContent='';box.style.display='none'},60000)}
async function rvSend(btn,kid,body){const m=btn.closest('.pmenu').querySelector('.rv_msg');m.style.color='';
 const r=await fetch('/settings/api/'+kid+'/reveal',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(body)});
 const j=await r.json();if(!j.ok){m.style.color='var(--err)';m.textContent=j.error;return}rvShow(btn,j.token)}
function rvPw(btn,kid){const p=btn.closest('.pmenu');const c=p.querySelector('.rv_code');
 rvSend(btn,kid,{password:p.querySelector('.rv_pw').value,code:c?c.value:''});p.querySelector('.rv_pw').value='';if(c)c.value=''}
async function rvPk(btn,kid){const m=btn.closest('.pmenu').querySelector('.rv_msg');
 try{let r=await fetch('/settings/api/reveal/options',{method:'POST',headers:{Accept:'application/json'}});let o=await r.json();if(o.ok===false)throw new Error(o.error);
  o.challenge=b64u.dec(o.challenge);(o.allowCredentials||[]).forEach(c=>c.id=b64u.dec(c.id));
  const cred=await navigator.credentials.get({publicKey:o});await rvSend(btn,kid,{credential:pkCredJSON(cred)})}
 catch(e){m.style.color='var(--err)';m.textContent=e.name==='NotAllowedError'?'Abgebrochen oder kein passender Passkey auf diesem Gerät.':(e.message||String(e))}}
if(window.PublicKeyCredential&&window.isSecureContext)document.querySelectorAll('.rvpk').forEach(b=>b.style.display='');
document.querySelectorAll('.rv_pw,.rv_code').forEach(i=>i.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();i.closest('.pmenu').querySelector('.btn.pri').click()}}));{% endraw %}
</script>

<form method="post" class="card"><h2>Neuen API-Key erstellen</h2>
<div class="row"><div><label>Name</label><input type="text" name="name" maxlength="60" placeholder="z. B. n8n, Home Assistant, Claude" required></div>
<div><label>Rolle (Rechte)</label><select name="role">{% for rid, r in roles.items() %}<option value="{{ rid }}" {{ "selected" if rid == "viewer" }}>{{ r.name }}{% if r.description %} – {{ r.description }}{% endif %}</option>{% endfor %}</select></div></div>
<div class="hint">Für Key-eigene Rechte unter <a href="/roles">Rollen</a> eine passende Rolle anlegen (z. B. „Home Assistant“: nur ansehen und starten, beschränkt auf bestimmte Aufgaben). Du kannst nur Rollen vergeben, deren Rechte du selbst hast.</div>
<div class="row"><div><label>Gültig bis (optional)</label><input type="date" name="expires"></div>
<div><label>Nur von diesen IP-Adressen (optional)</label><input type="text" name="ips" placeholder="z. B. 192.168.1.20, 10.0.0.0/24"></div></div>
<div class="row"><div><label>Sprache der API-Antworten</label><select name="lang"><option value="">{{ _("Wie der Benutzer") }} ({{ g.user }})</option>{% for c, n in LANGS() %}<option value="{{ c }}" {{ "selected" if c == '' }}>{{ n }}</option>{% endfor %}</select></div><div></div></div>
<div class="hint">Meldungen, Swagger-Beschreibungen und MCP-Tool-Texte. „Wie der Benutzer“ nimmt die Sprache aus dessen Konto (Mein Konto → Sprache), ohne bekannten Benutzer Englisch. Einzelne Anfragen können sie mit <code>?lang=en</code> oder dem Header <code>Accept-Language</code> überschreiben.</div>
<div class="hint">Leer = unbegrenzt bzw. von überall. Hinter einem Reverse-Proxy muss unter Allgemein „Reverse-Proxy“ an sein, sonst sieht MirrorSync nur die Adresse des Proxys.</div>
<p style="margin-top:14px"><button class="btn pri">Key erstellen</button></p></form>
{% endblock %}
""",
"api_docs.html": r"""<!doctype html><html lang="{{ lang_code() }}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MirrorSync API</title><link rel="icon" href="/static/favicon.svg" type="image/svg+xml"><link rel="manifest" href="/manifest.webmanifest">
<script>(function(){let t=null;try{t=localStorage.getItem('ms-theme')}catch(e){}if(t!=='light'&&t!=='dark')t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.dataset.theme=t})()</script>
<link rel="stylesheet" href="{{ sw }}/swagger-ui.css">
<style>:root{--bg:#fff;--fg:#0f172a;--mut:#64748b;--bd:#e5e7eb;--acc:#4f46e5;color-scheme:light}
html[data-theme=dark]{--bg:#09090b;--fg:#ececf1;--mut:#a1a1aa;--bd:#27272a;--acc:#818cf8;color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--fg)}.top{display:flex;gap:12px;align-items:center;padding:10px 18px;border-bottom:1px solid var(--bd);font:14px system-ui,sans-serif;flex-wrap:wrap}
.top a,.top button{color:var(--acc);text-decoration:none;background:none;border:1px solid var(--bd);border-radius:8px;padding:5px 10px;font:inherit;cursor:pointer}.top a{border:0;padding:0}
/* Swagger UI im Dunkelmodus */
html[data-theme=dark] .swagger-ui,html[data-theme=dark] .swagger-ui .info .title,html[data-theme=dark] .swagger-ui .info p,html[data-theme=dark] .swagger-ui .info li,html[data-theme=dark] .swagger-ui .info table,
html[data-theme=dark] .swagger-ui .opblock-tag,html[data-theme=dark] .swagger-ui .opblock .opblock-summary-description,html[data-theme=dark] .swagger-ui .opblock .opblock-summary-operation-id,
html[data-theme=dark] .swagger-ui .opblock .opblock-summary-path,html[data-theme=dark] .swagger-ui .opblock .opblock-summary-path__deprecated,html[data-theme=dark] .swagger-ui .opblock-description-wrapper p,
html[data-theme=dark] .swagger-ui .opblock-external-docs-wrapper p,html[data-theme=dark] .swagger-ui .opblock-title_normal p,html[data-theme=dark] .swagger-ui .opblock .opblock-section-header h4,
html[data-theme=dark] .swagger-ui .opblock .opblock-section-header>label,html[data-theme=dark] .swagger-ui .tab li,html[data-theme=dark] .swagger-ui table thead tr th,html[data-theme=dark] .swagger-ui table thead tr td,
html[data-theme=dark] .swagger-ui .parameter__name,html[data-theme=dark] .swagger-ui .parameter__type,html[data-theme=dark] .swagger-ui .parameter__in,html[data-theme=dark] .swagger-ui .parameter__extension,
html[data-theme=dark] .swagger-ui .response-col_status,html[data-theme=dark] .swagger-ui .response-col_links,html[data-theme=dark] .swagger-ui .responses-inner h4,html[data-theme=dark] .swagger-ui .responses-inner h5,
html[data-theme=dark] .swagger-ui .model-title,html[data-theme=dark] .swagger-ui .model,html[data-theme=dark] .swagger-ui section.models h4,html[data-theme=dark] .swagger-ui .scheme-container .schemes>label,
html[data-theme=dark] .swagger-ui .btn,html[data-theme=dark] .swagger-ui label,html[data-theme=dark] .swagger-ui .markdown p,html[data-theme=dark] .swagger-ui .markdown li,html[data-theme=dark] .swagger-ui .renderedMarkdown p,
html[data-theme=dark] .swagger-ui .dialog-ux .modal-ux-header h3,html[data-theme=dark] .swagger-ui .dialog-ux .modal-ux-content p,html[data-theme=dark] .swagger-ui .dialog-ux .modal-ux-content h4,
html[data-theme=dark] .swagger-ui .prop-type,html[data-theme=dark] .swagger-ui .prop-format,html[data-theme=dark] .swagger-ui .model-toggle:after,html[data-theme=dark] .swagger-ui .response-control-media-type__title,
html[data-theme=dark] .swagger-ui .responses-table .response-col_description,html[data-theme=dark] .swagger-ui .info .base-url,html[data-theme=dark] .swagger-ui .opblock-tag small{color:var(--fg)}
html[data-theme=dark] .swagger-ui .scheme-container,html[data-theme=dark] .swagger-ui .opblock .opblock-section-header,html[data-theme=dark] .swagger-ui .dialog-ux .modal-ux,
html[data-theme=dark] .swagger-ui .dialog-ux .modal-ux-header,html[data-theme=dark] .swagger-ui section.models .model-container,html[data-theme=dark] .swagger-ui .model-box{background:#18181b;box-shadow:none}
html[data-theme=dark] .swagger-ui section.models,html[data-theme=dark] .swagger-ui .opblock-tag,html[data-theme=dark] .swagger-ui .dialog-ux .modal-ux,html[data-theme=dark] .swagger-ui .dialog-ux .modal-ux-header,
html[data-theme=dark] .swagger-ui table thead tr td,html[data-theme=dark] .swagger-ui table thead tr th{border-color:var(--bd)}
html[data-theme=dark] .swagger-ui input[type=text],html[data-theme=dark] .swagger-ui input[type=password],html[data-theme=dark] .swagger-ui input[type=email],html[data-theme=dark] .swagger-ui input[type=file],
html[data-theme=dark] .swagger-ui textarea,html[data-theme=dark] .swagger-ui select{background:#111113;color:var(--fg);border-color:#3f3f46}
html[data-theme=dark] .swagger-ui .btn{border-color:#52525b}html[data-theme=dark] .swagger-ui .btn.authorize,html[data-theme=dark] .swagger-ui .btn.authorize svg{color:#4ade80;fill:#4ade80;border-color:#4ade80}
html[data-theme=dark] .swagger-ui svg:not(:root){fill:var(--fg)}html[data-theme=dark] .swagger-ui .opblock .opblock-summary-method svg,html[data-theme=dark] .swagger-ui .opblock-summary-control svg{fill:var(--fg)}
html[data-theme=dark] .swagger-ui .info a,html[data-theme=dark] .swagger-ui a.nostyle,html[data-theme=dark] .swagger-ui .info .title small pre{color:var(--acc)}
html[data-theme=dark] .swagger-ui .info .title small{background:#3f3f46}html[data-theme=dark] .swagger-ui .opblock-body pre.microlight,html[data-theme=dark] .swagger-ui .highlight-code>.microlight{background:#111113!important}
html[data-theme=dark] .swagger-ui .markdown code,html[data-theme=dark] .swagger-ui .renderedMarkdown code{background:#27272a;color:#f0abfc}
html[data-theme=dark] .swagger-ui .opblock.opblock-get{background:rgba(97,175,254,.08)}html[data-theme=dark] .swagger-ui .opblock.opblock-post{background:rgba(73,204,144,.08)}
html[data-theme=dark] .swagger-ui .opblock.opblock-put{background:rgba(252,161,48,.08)}html[data-theme=dark] .swagger-ui .opblock.opblock-delete{background:rgba(249,62,62,.08)}
html[data-theme=dark] .swagger-ui .opblock.opblock-patch{background:rgba(80,227,194,.08)}html[data-theme=dark] .swagger-ui .opblock .tab-header .tab-item.active h4 span:after{background:var(--mut)}
html[data-theme=dark] .swagger-ui .parameter__name.required:after,html[data-theme=dark] .swagger-ui .parameter__name.required span{color:#f87171}
html[data-theme=dark] .swagger-ui .model .property.primitive,html[data-theme=dark] .swagger-ui .model-hint{color:var(--mut)}html[data-theme=dark] .swagger-ui .loading-container .loading:after{color:var(--fg)}
html[data-theme=dark] .swagger-ui .response-col_description__inner p,html[data-theme=dark] .swagger-ui .errors-wrapper{color:var(--fg)}html[data-theme=dark] .swagger-ui .copy-to-clipboard{background:#3f3f46}
</style></head><body>
<div class="top"><b>MirrorSync API {{ VERSION }}</b><span style="flex:1"></span><button type="button" id="thb" onclick="msTheme()"></button><a href="/settings/api">API-Keys</a><a href="/">Zurück zur GUI</a></div>
<div id="ui"></div>
<script src="{{ sw }}/swagger-ui-bundle.js"></script>
<script>const TL={dark:'☀ {{ _("Hell") }}',light:'☾ {{ _("Dunkel") }}'};function msThl(){document.getElementById('thb').textContent=TL[document.documentElement.dataset.theme]}
function msTheme(){const r=document.documentElement;r.dataset.theme=r.dataset.theme==='dark'?'light':'dark';try{localStorage.setItem('ms-theme',r.dataset.theme)}catch(e){}msThl()}msThl();
window.ui=SwaggerUIBundle({url:'/api/v1/openapi.json',dom_id:'#ui',deepLinking:true,persistAuthorization:true,tryItOutEnabled:false,syntaxHighlight:{theme:document.documentElement.dataset.theme==='dark'?'monokai':'agate'}});</script>
</body></html>
""",
"denied.html": r"""{% extends "base.html" %}{% block title %}Keine Berechtigung{% endblock %}{% block body %}
<div class="card"><div class="empty">{{ ICON.lock }}<p style="font-size:15px;color:var(--fg)">Dafür fehlen dir die Rechte.</p>
<p>Deine Rolle ist <b>{{ role_name(g.role) }}</b>.{% if perm %} Benötigt wird das Recht „{{ perm }}“.{% endif %} Ein Admin kann die Rolle unter Einstellungen → Rollen anpassen.</p>
<p><a class="btn" href="/">Zur Übersicht</a></p></div></div>
{% endblock %}
""",
"versions.html": r"""{% extends "base.html" %}{% block title %}Papierkorb: {{ job.name }}{% endblock %}
{% block subtitle %}<p class="path">{{ data.base }}</p>{% endblock %}
{% block actions %}<a class="btn" href="/job/{{ job_id }}/log">Log</a><a class="btn" href="/job/{{ job_id }}">Aufgabe</a>{% endblock %}
{% block body %}
{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
{% if not job.versioning %}<div class="msg info">Papierkorb/Versionierung ist bei dieser Aufgabe aus. Gelöschte und überschriebene Dateien werden dann direkt entfernt. Einschalten unter <a href="/job/{{ job_id }}">Aufgabe → Optionen</a>.{% if data.stamps %} Ältere Stände sind noch da.{% endif %}</div>{% endif %}
<div class="card">
<form method="get" class="row" style="align-items:flex-end;flex-wrap:wrap">
{% if bisync %}<div style="flex:0 0 180px"><label>Seite</label><select name="side"><option value="b" {{ "selected" if side == "b" }}>Seite B (Ziel)</option><option value="a" {{ "selected" if side == "a" }}>Seite A (Quelle)</option></select></div>{% endif %}
<div style="flex:2 1 260px"><label for="q">Dateiname oder Pfad enthält</label><input type="text" name="q" id="q" value="{{ q }}" placeholder="z. B. rechnung oder Fotos/2024" autofocus></div>
<div style="flex:1 1 220px"><label for="stamp">Stand</label><select name="stamp" id="stamp"><option value="">alle Stände</option>{% for st in data.stamps %}<option value="{{ st }}" {{ "selected" if st == stamp }}>{{ st|stamp }}</option>{% endfor %}</select></div>
<div style="flex:0 0 auto"><input type="hidden" name="any" value="1"><button class="btn pri">Suchen</button></div></form>
<p class="hint">{{ _("{0} Stände vorhanden.", data.stamps|length) }} Jeder Stand enthält die Dateien, die bei einem Lauf zu diesem Zeitpunkt gelöscht oder überschrieben wurden, in ihrer alten Fassung. Suche ohne Stand durchsucht alle (kann bei vielen Ständen dauern).</p>
</div>
{% if data.files %}<form method="post" action="/job/{{ job_id }}/versions/restore" class="card">
<input type="hidden" name="q" value="{{ q }}"><input type="hidden" name="stamp" value="{{ stamp }}"><input type="hidden" name="side" value="{{ side }}">
<div class="card-head"><h2>{{ _("{0} Dateien", data.files|length) }}{% if data.truncated %} <small class="mut">(gekürzt, bitte genauer suchen)</small>{% endif %}</h2>
<label class="check" style="margin:0"><input type="checkbox" onclick="document.querySelectorAll('.vsel').forEach(c=>c.checked=this.checked)"> alle auswählen</label></div>
<table><tr><th></th><th>Datei</th><th>Stand (gelöscht/ersetzt am)</th><th class="hide-sm">Größe</th><th class="hide-sm">Geändert</th><th></th></tr>
{% for f in data.files %}<tr><td style="width:28px"><input type="checkbox" class="vsel" name="item" value="{{ f.stamp }}|{{ f.path }}"></td>
<td><span class="path" style="color:var(--fg)">{{ f.path }}</span></td><td><small>{{ f.stamp|stamp }}</small></td>
<td class="hide-sm num">{{ f.size|hbytes if f.size is not none else "–" }}</td><td class="hide-sm"><small>{{ f.mod }}</small></td>
<td style="white-space:nowrap"><a class="btn sm" href="/job/{{ job_id }}/versions/download?stamp={{ f.stamp|urlencode }}&path={{ f.path|urlencode }}&side={{ side }}" title="Herunterladen">↓</a></td></tr>{% endfor %}</table>
<div class="row" style="align-items:flex-end;margin-top:12px;flex-wrap:wrap">
<div style="flex:1 1 320px"><label>Wiederherstellen nach</label><select name="target">
<option value="source">{{ "Seite A" if bisync else "Quelle" }}: {{ job.source }} (empfohlen)</option>
<option value="dest">{{ "Seite B" if bisync else "Ziel" }}: {{ job.dest }}</option></select></div>
<div style="flex:0 0 auto"><label class="check"><input type="checkbox" name="overwrite"> Vorhandene überschreiben</label></div>
<div style="flex:0 0 auto"><button class="btn pri">Ausgewählte wiederherstellen</button></div></div>
<p class="hint">In die {{ "Seiten" if bisync else "Quelle" }} zurückgeholt, wird die Datei beim nächsten Lauf wieder ins Ziel gespiegelt.{% if not bisync %} Nur ins Ziel zurückgelegt, löscht oder überschreibt der nächste Lauf sie wieder, wenn sie in der Quelle fehlt oder anders ist.{% endif %} Die Datei bleibt zusätzlich im Papierkorb.</p>
</form>{% elif q or stamp %}<div class="card"><div class="empty">Nichts gefunden.</div></div>{% endif %}
{% endblock %}""",

"usage.html": r"""{% extends "base.html" %}{% block title %}Platzbedarf: {{ job.name }}{% endblock %}
{% block subtitle %}<p class="path">{{ u.path or (job.source if side == "source" else job.dest) }}</p>{% endblock %}
{% block actions %}<a class="btn" href="/job/{{ job_id }}/log">Log</a><a class="btn" href="/job/{{ job_id }}">Aufgabe</a>{% endblock %}
{% block body %}
<div class="tabs"><a href="?side=source" class="{{ 'active' if side == 'source' }}">{{ "Seite A" if job.direction == "bisync" else "Quelle" }}</a><a href="?side=dest" class="{{ 'active' if side == 'dest' }}">{{ "Seite B" if job.direction == "bisync" else "Ziel" }}</a></div>
<div class="card"><div class="card-head"><div><h2>Größte Ordner und Dateien</h2>
<p class="mut" style="margin:0">{% if u.state == "läuft" %}{{ _("Wird gezählt … {0} Dateien, {1} bisher.", u.files, u.bytes|hbytes) }}{% elif u.at %}{{ _("Stand {0}: {1} Dateien, {2}.", u.at|dt, u.files, u.bytes|hbytes) }}{% else %}Noch nicht ermittelt. Die Analyse liest einmal alle Ordner (mit den Filtern der Aufgabe).{% endif %}</p></div>
{% if u.state != "läuft" %}<form method="post"><input type="hidden" name="side" value="{{ side }}"><button class="btn pri">{{ "Neu ermitteln" if u.at else "Jetzt ermitteln" }}</button></form>{% endif %}</div>
{% if u.state == "fehler" %}<div class="msg err">{{ u.error }}</div>{% endif %}
{% if u.children is defined %}
<p class="fbcrumbs"><a href="?side={{ side }}">{{ "Seite A" if side == "source" and job.direction == "bisync" else ("Quelle" if side == "source" else ("Seite B" if job.direction == "bisync" else "Ziel")) }}</a>{% set acc = namespace(p="") %}{% for part in (u.sub or "").strip("/").split("/") if part %}{% set acc.p = (acc.p ~ "/" ~ part).lstrip("/") %}<span class="sep">/</span><a href="?side={{ side }}&path={{ acc.p|urlencode }}">{{ part }}</a>{% endfor %}
 <small class="mut">· {{ u.dir_bytes|hbytes }}, {{ u.dir_files }} Dateien</small></p>
{% if u.children %}<table><tr><th>Ordner</th><th style="width:40%">Anteil</th><th class="num">Größe</th><th class="num hide-sm">Dateien</th></tr>
{% for c in u.children %}{% set pct = (c.bytes * 100 / u.dir_bytes) if u.dir_bytes else 0 %}<tr class="click" onclick="location='?side={{ side }}&path={{ c.path|urlencode }}'"><td><a href="?side={{ side }}&path={{ c.path|urlencode }}">📁 {{ c.name }}</a></td>
<td><div class="fm-bar" style="width:100%"><i style="width:{{ pct|round(1) }}%;background:var(--acc)"></i></div><small class="mut">{{ pct|round(1) }} %</small></td>
<td class="num">{{ c.bytes|hbytes }}</td><td class="num hide-sm">{{ c.files }}</td></tr>{% endfor %}</table>{% else %}<p class="mut">Keine Unterordner.</p>{% endif %}
{% if u.top_files %}<h3 style="margin-top:18px">Größte Dateien{% if u.sub %} in diesem Ordner{% endif %}</h3><table><tr><th>Datei</th><th class="num">Größe</th></tr>
{% for f in u.top_files %}<tr><td><span class="path" style="color:var(--fg)">{{ f.path }}</span></td><td class="num">{{ f.bytes|hbytes }}</td></tr>{% endfor %}</table>{% endif %}
{% endif %}</div>
<div class="card"><h2>Am häufigsten übertragen</h2>
<p class="mut" style="margin-top:-4px">{{ _("Aus den Logs der letzten {0} Tage ({1} Läufe): welche Ordner und Dateien immer wieder kopiert werden und damit Übertragungszeit kosten.", hot.days, hot.runs) }}</p>
{% if hot.folders %}<div class="row" style="flex-wrap:wrap"><div style="flex:1 1 300px"><table><tr><th>Ordner (oberste Ebene)</th><th class="num">Übertragungen</th></tr>{% for x in hot.folders %}<tr><td>📁 {{ x.name }}</td><td class="num">{{ x.count }}</td></tr>{% endfor %}</table></div>
<div style="flex:1 1 300px">{% if hot.files %}<table><tr><th>Datei (mehrfach übertragen)</th><th class="num">Mal</th></tr>{% for x in hot.files %}<tr><td><span class="path" style="color:var(--fg)">{{ x.path }}</span></td><td class="num">{{ x.count }}</td></tr>{% endfor %}</table>{% endif %}</div></div>
{% else %}<p class="mut">In den aufbewahrten Logs wurde nichts übertragen.</p>{% endif %}</div>
{% endblock %}""",

"stats.html": r"""{% extends "base.html" %}{% block title %}Statistik{% endblock %}
{% block subtitle %}<p>Übertragungen pro Monat, z. B. für Verbindungen mit Datenvolumen-Limit.</p>{% endblock %}
{% block body %}
{% if vol %}<div class="card"><h2>Datenvolumen {{ vol.month[5:] }}/{{ vol.month[:4] }}</h2>
<div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap"><span><b>{{ vol.used|hbytes }}</b> von {{ vol.limit|hbytes }}</span><span class="{{ 'fehler' if vol.exceeded else ('gestoppt' if vol.warn else 'ok') }}">{{ vol.pct }} %</span></div>
<div class="fm-bar" style="width:100%;height:10px;margin-top:6px"><i style="width:{{ [vol.pct,100]|min }}%;background:{{ 'var(--err)' if vol.exceeded else ('var(--warn)' if vol.warn else 'var(--ok)') }}"></i></div>
{% if vol.exceeded and vol.stop %}<p class="fehler" style="margin-bottom:0">Limit erreicht: Automatische Läufe sind bis zum Monatsende angehalten.</p>{% endif %}
{% if can("system.settings") %}<p class="hint"><a href="/settings/general#monitor">Limit ändern</a></p>{% endif %}</div>{% endif %}
{% if not months %}<div class="card"><div class="empty">Noch keine Läufe gezählt.</div></div>{% else %}
{% set mx = months|map(attribute="totals")|map(attribute="bytes")|max %}
<div class="card"><h2>Verlauf</h2><table><tr><th>Monat</th><th style="width:38%">Übertragen</th><th class="num">Läufe</th><th class="num">ok</th><th class="num">Fehler</th><th class="num hide-sm">Kopiert</th><th class="num hide-sm">Gelöscht</th><th class="num hide-sm">Laufzeit</th></tr>
{% for m in months %}{% set t = m.totals %}<tr class="click" onclick="document.getElementById('m{{ m.month }}').open=true;location.hash='m{{ m.month }}'">
<td><b>{{ m.month[5:] }}/{{ m.month[:4] }}</b></td><td><div class="fm-bar" style="width:100%"><i style="width:{{ (t.bytes * 100 / mx)|round(1) if mx else 0 }}%;background:var(--acc)"></i></div><small>{{ t.bytes|hbytes }}</small></td>
<td class="num">{{ t.runs }}</td><td class="num ok">{{ t.ok }}</td><td class="num {{ 'err' if t.fail }}">{{ t.fail }}</td><td class="num hide-sm">{{ t.copied }}</td><td class="num hide-sm">{{ t.deleted }}</td>
<td class="num hide-sm">{{ (t.duration // 3600) }} h {{ (t.duration % 3600) // 60 }} min</td></tr>{% endfor %}</table></div>
{% for m in months %}<details class="tpl card" id="m{{ m.month }}" {{ "open" if loop.first }} style="padding:0"><summary><b>{{ m.month[5:] }}/{{ m.month[:4] }}</b> <span class="mut">· {{ m.totals.bytes|hbytes }} · {{ m.totals.runs }} Läufe</span></summary><div class="tplbody">
<table><tr><th>Aufgabe</th><th class="num">Übertragen</th><th class="num">Läufe</th><th class="num">ok</th><th class="num">Fehler</th><th class="num hide-sm">Testläufe</th><th class="num hide-sm">Prüfläufe ok</th><th class="num hide-sm">Laufzeit</th></tr>
{% for j in m.jobs %}<tr><td>{{ j.name }}</td><td class="num">{{ j.bytes|hbytes }}</td><td class="num">{{ j.runs }}</td><td class="num">{{ j.ok }}</td><td class="num {{ 'err' if j.fail }}">{{ j.fail }}</td>
<td class="num hide-sm">{{ j.dry }}</td><td class="num hide-sm">{{ j.verify_ok }}{% if j.verify_fail %} / <span class="fehler">{{ j.verify_fail }} ✖</span>{% endif %}</td><td class="num hide-sm">{{ (j.duration // 3600) }} h {{ (j.duration % 3600) // 60 }} min</td></tr>{% endfor %}</table></div></details>{% endfor %}
{% endif %}
<p class="hint">Gezählt werden echte Läufe (Testläufe nur in der Spalte „Testläufe“, ohne Datenmenge). Live-Runden ohne Änderung zählen nicht. Die Zahlen bleiben erhalten, auch wenn alte Logs gelöscht werden. Als Kennzahlen für Grafana: <code>/metrics</code>.</p>
{% endblock %}""",

"changelog.html": r"""{% extends "base.html" %}{% block title %}Versionshinweise{% endblock %}
{% block subtitle %}<p>Was sich in jeder Version von MirrorSync geändert hat. Installiert ist v{{ VERSION }}.</p>{% endblock %}
{% block actions %}<a class="btn" href="{{ release_url }}" target="_blank" rel="noopener">Auf GitHub</a>{% endblock %}
{% block body %}
<div class="card" style="padding:10px 16px"><div class="chips" style="margin:0">{% for e in items[:40] %}<a class="chip {{ 'active' if e.version == VERSION }}" href="#v{{ e.version }}">v{{ e.version }}</a>{% endfor %}</div></div>
{% for e in items %}<div class="card cl" id="v{{ e.version }}"><div class="card-head" style="margin-bottom:4px"><h2>v{{ e.version }}{% if e.version == VERSION %} <span class="tag ok">installiert</span>{% endif %}</h2><small class="mut">{{ e.date }}</small></div>
<div class="clbody">{{ e.html }}</div></div>{% else %}<div class="card"><div class="empty">Keine Versionshinweise gefunden (CHANGELOG.md fehlt im Image).</div></div>{% endfor %}
<style>.clbody ul{margin:6px 0 10px;padding-left:20px}.clbody li{margin:3px 0}.clbody p{margin:8px 0}.clbody h4{margin:12px 0 4px}</style>
{% endblock %}""",

"offline.html": r"""<!doctype html><html lang="{{ lang_code() }}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MirrorSync · offline</title><meta name="theme-color" content="#4f46e5"><link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;font:15px/1.5 system-ui,sans-serif;background:#f6f7f9;color:#0f172a;text-align:center;padding:20px}
@media (prefers-color-scheme:dark){body{background:#09090b;color:#ececf1}}img{width:72px;height:72px}button{margin-top:14px;padding:9px 16px;border-radius:8px;border:0;background:#4f46e5;color:#fff;font:inherit;cursor:pointer}</style></head>
<body><div><img src="/static/favicon.svg" alt=""><h1 style="font-size:20px">MirrorSync ist gerade nicht erreichbar</h1><p>Keine Verbindung zum Server. Prüfe das Netzwerk oder ob der Container läuft.</p><button onclick="location.reload()">Neu laden</button></div></body></html>""",

"help.html": r"""{% extends "base.html" %}{% block title %}Hilfe{% endblock %}{% block subtitle %}<p>Alles, was du in MirrorSync einstellen kannst, kurz erklärt. Mit Anleitungen für API, MCP, Uptime Kuma und Home Assistant.</p>{% endblock %}{% block body %}{% include "tabs.html" %}
<style>
.hsearch{position:sticky;top:0;z-index:5;background:var(--bg);padding:4px 0 10px}
.hsearch input{font-size:16px;padding:11px 14px;width:100%;max-width:none;box-sizing:border-box}
.hlayout{display:flex;gap:18px;align-items:flex-start}
.htoc{flex:0 0 240px;position:sticky;top:70px;max-height:calc(100vh - 90px);overflow:auto;font-size:13.5px}
.htoc a{display:block;padding:5px 8px;border-radius:7px;color:var(--fg);text-decoration:none}
.htoc a:hover{background:var(--card2)}
.hmain{flex:1;min-width:0}
.hsec{scroll-margin-top:70px}
.hsec h2{display:flex;align-items:center;gap:8px}
.hsec h2 .go{margin-left:auto;font-size:13px;font-weight:400}
.hent{padding:10px 0;border-top:1px solid var(--bd)}
.hent:first-of-type{border-top:0}
.hent h3{margin:0 0 4px;font-size:15px}
.hent p{margin:0;line-height:1.55}
.hent pre{position:relative;margin:8px 0 0;white-space:pre;overflow:auto}
.hent pre button{position:absolute;top:6px;right:6px}
mark{background:#fde68a;color:#111;border-radius:3px;padding:0 1px}
@media (max-width:900px){.htoc{display:none}}
</style>
<div class="hsearch"><input type="search" id="hq" placeholder="Hilfe durchsuchen, z. B. Löschwarnung, Cron, Uptime Kuma, MCP" autocomplete="off" autofocus>
<div class="hint" id="hcount" style="margin-top:6px"></div></div>
<div class="hlayout"><nav class="htoc card" id="htoc">{% for s in sections %}<a href="#{{ s.id }}" data-s="{{ s.id }}">{{ s.icon }} {{ s.title }}</a>{% endfor %}</nav>
<div class="hmain">{% for s in sections %}<div class="card hsec" id="{{ s.id }}"><h2>{{ s.icon }} {{ s.title }}{% if s.link %}<a class="go" href="{{ s.link }}">Zur Seite →</a>{% endif %}</h2>
{% for e in s.entries %}<div class="hent" id="{{ e.id }}"><h3>{{ e.title }}</h3><p>{{ e.text }}</p>{% if e.code %}<pre><code>{{ e.code }}</code><button type="button" class="btn sm" onclick="hCopy(this)">Kopieren</button></pre>{% endif %}</div>{% endfor %}</div>{% endfor %}
<div class="card" id="hnone" hidden><div class="empty">Nichts gefunden. Versuche einen anderen Begriff.</div></div></div></div>
<script>
(function(){
const q=document.getElementById('hq'),cnt=document.getElementById('hcount'),none=document.getElementById('hnone');
const ents=[...document.querySelectorAll('.hent')],secs=[...document.querySelectorAll('.hsec')];
ents.forEach(e=>{e._h=[...e.querySelectorAll('h3,p')].map(x=>[x,x.innerHTML]);e._t=e.textContent.toLowerCase()+' '+e.closest('.hsec').querySelector('h2').textContent.toLowerCase()});
const T_HITS={{ _("{0} Treffer")|tojson }};
function esc(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}
function mark(el,html,words){if(!words.length){el.innerHTML=html;return}
 const re=new RegExp('('+words.map(esc).join('|')+')','gi');
 el.innerHTML=html.split(/(<[^>]+>)/).map(p=>p.startsWith('<')?p:p.replace(re,'<mark>$1</mark>')).join('')}
function run(){const words=q.value.toLowerCase().split(/\s+/).filter(Boolean);let n=0;
 ents.forEach(e=>{const ok=words.every(w=>e._t.includes(w));e.hidden=!ok;if(ok)n++;e._h.forEach(([el,h])=>mark(el,h,ok?words:[]))});
 secs.forEach(s=>{const vis=[...s.querySelectorAll('.hent')].some(e=>!e.hidden);s.hidden=!vis;const a=document.querySelector('.htoc a[data-s="'+s.id+'"]');if(a)a.hidden=!vis});
 none.hidden=n>0;cnt.textContent=words.length?T_HITS.replace('{0}',n):'';
 try{history.replaceState(null,'',words.length?'?q='+encodeURIComponent(q.value):location.pathname+location.hash)}catch(e){}}
q.addEventListener('input',run);
const p=new URLSearchParams(location.search).get('q');if(p){q.value=p;run()}
if(location.hash){const t=document.getElementById(location.hash.slice(1));if(t)setTimeout(()=>t.scrollIntoView(),50)}
window.hCopy=function(b){const t=b.parentElement.querySelector('code').textContent;const done=()=>{const o=b.textContent;b.textContent='✓';setTimeout(()=>b.textContent=o,1200)};
 if(navigator.clipboard)navigator.clipboard.writeText(t).then(done).catch(()=>{});else{const a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove();done()}}
})();
</script>
{% endblock %}""",
"users.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}
{% block actions %}{% if can("users.manage") %}<a class="btn pri" href="/users/new">{{ ICON.plus }} Neuer Benutzer</a>{% endif %}{% endblock %}
{% block body %}{% include "tabs.html" %}
{% if msg %}<div class="msg info">{{ msg }}</div>{% endif %}
<div class="card" style="padding:6px 8px">
{% if fails %}<div class="msg err" style="margin:6px 4px 10px">⚠️ {{ fails }} unbestätigte fehlgeschlagene Anmeldung{{ "en" if fails != 1 }}. <a href="/users/log?f=new">Ansehen und bestätigen</a></div>{% endif %}
{% for grp in conflicts %}<div class="msg info" style="margin:6px 4px 10px">Die Benutzer <b>{{ grp|join(", ") }}</b> unterscheiden sich nur in Groß-/Kleinschreibung. Seit 1.9.0 zählt die Schreibweise bei der Anmeldung nicht mehr, deshalb klappt die Anmeldung für sie nur mit der exakten Schreibweise. Bitte einen davon löschen.</div>{% endfor %}
<table><tr><th>Benutzer</th><th>Rolle</th><th>2FA / Passkey</th><th class="hide-sm">Letzte Anmeldung</th><th style="text-align:right">Aktionen</th></tr>
{% for u in rows %}<tr>
<td><div style="display:flex;gap:10px;align-items:center"><span class="avatar" style="{{ 'opacity:.45' if u.why }}">{{ u.name[:1]|upper }}</span><div><b>{{ u.name }}</b>{% if u.name == g.user %} <small>(du)</small>{% endif %}
{% if u.why == "deaktiviert" %} <span class="tag fehler">deaktiviert{% if u.disabled_by %} ({{ u.disabled_by }}){% endif %}</span>
{% elif u.why == "gesperrt" %} <span class="tag gestoppt">gesperrt{% if u.auto_lock_until and u.auto_lock_until > (u.lock_until or '') %} bis {{ u.auto_lock_until|dt }}{% elif u.lock_until %} bis {{ u.lock_until|dt }}{% endif %}</span>
{% elif u.planned %} <span class="tag">Sperre ab {{ u.lock_from|dt }}</span>{% endif %}
{% if u.fail_count %}<br><small class="fehler">{{ u.fail_count }} Fehlversuch{{ "e" if u.fail_count != 1 }}</small>{% endif %}
<br><small>angelegt {{ u.created }}</small></div></div></td>
<td><span class="tag {{ 'laeuft' if u.role == 'admin' else ('ok' if u.role in roles else 'fehler') }}">{{ roles[u.role].name if u.role in roles else u.role ~ ' (fehlt)' }}</span>{% if u.group_names %}<br><small class="mut">{{ u.group_names|join(", ") }}</small>{% endif %}</td>
<td>{% if u.totp_enabled %}<span class="tag ok">aktiv</span><br><small>{{ u.backup_left }} Backup-Codes</small>{% elif u.must2fa %}<span class="tag gestoppt">Pflicht, noch nicht eingerichtet</span>{% else %}<span class="tag">aus</span>{% endif %}{% if u.must2fa and u.totp_enabled %}<br><small>Pflicht</small>{% endif %}{% if u.n_passkeys %}<br><small>🔑 {{ u.n_passkeys }} Passkey{{ "s" if u.n_passkeys != 1 }}</small>{% endif %}</td>
<td class="hide-sm"><small>{% if u.last_login %}{{ u.last_login }}<br>{% if u.last_ip %}<code>{{ u.last_ip }}</code> {{ u.last_flag }} {{ u.last_country }}{% endif %}{% else %}noch nie{% endif %}</small></td>
<td style="text-align:right;white-space:nowrap">{% if can("users.manage") %}{% if u.disabled_by or (u.why == "gesperrt" and u.auto_lock_until) %}<form class="inline" method="post" action="/users/{{ u.name }}/unlock"><button class="btn sm pri">Entsperren</button></form> {% endif %}<a class="btn sm" href="/users/{{ u.name }}/edit">Bearbeiten</a>
{% if u.name != g.user %}<form class="inline" method="post" action="/users/{{ u.name }}/delete" onsubmit="return confirm('Benutzer {{ u.name }} löschen?')"><button class="btn sm del">Entfernen</button></form>{% endif %}{% endif %}</td>
</tr>{% endfor %}</table></div>
<div class="card"><h3>Rollen</h3>
{% for r in roles.values() %}<p style="margin:8px 0"><b>{{ r.name }}</b>: <span class="mut">{{ r.description }}</span></p>{% endfor %}
<p>{% if can("roles.manage") %}<a class="btn sm" href="/roles">Rollen verwalten</a> {% endif %}<a class="btn sm" href="/users/log">Anmeldeverlauf</a></p>
<p class="hint">2FA richtet jeder Benutzer selbst unter „Mein Konto“ ein. Verliert jemand sein Handy und alle Backup-Codes, kann ein Admin die 2FA hier unter „Bearbeiten“ zurücksetzen.</p></div>
{% endblock %}
""",
"user_edit.html": r"""{% extends "base.html" %}{% block title %}{{ name if name else "Neuer Benutzer" }}{% endblock %}
{% block body %}{% include "tabs.html" %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
<form method="post" class="card">
<h2>{{ "Benutzer bearbeiten" if name else "Neuer Benutzer" }}</h2>
<label>Benutzername</label><input type="text" name="name" value="{{ name or form.get('name','') }}" {{ "disabled" if name else "required autofocus" }} autocomplete="off">
<label>Rolle</label><select name="role">{% for rid, r in roles.items() %}<option value="{{ rid }}" {{ "selected" if (form.get('role') or u.role) == rid }}>{{ r.name }}{% if r.description %} – {{ r.description }}{% endif %}</option>{% endfor %}</select>
<div class="row"><div><label>{{ "Neues Passwort (leer = unverändert)" if name else "Passwort" }}</label><input type="password" name="password" autocomplete="new-password" {{ "" if name else "required" }}></div>
<div><label>Passwort wiederholen</label><input type="password" name="password2" autocomplete="new-password" {{ "" if name else "required" }}></div></div>
<div class="hint">Mindestens 8 Zeichen.{% if name %} Bei Änderung von Passwort oder Rolle wird der Benutzer überall abgemeldet.{% endif %}</div>
{% if can("groups.manage") and all_groups %}<h3 style="margin-top:22px">Gruppen</h3><input type="hidden" name="grp_form" value="1">
<div class="picklist" style="margin:0">{% for gid, x in all_groups %}<label class="check"><input type="checkbox" name="grp" value="{{ gid }}" {{ "checked" if gid in my_groups }} {{ "disabled" if not x.editable }}> {{ x.name }}{% if x.description %} <small class="mut">– {{ x.description }}</small>{% endif %}</label>{% endfor %}</div>
<div class="hint">Gruppen geben zusätzliche Rechte und Sichtbarkeit. Ausgegraut: Gruppe hat Rechte, die du selbst nicht hast.</div>
{% elif my_group_names %}<h3 style="margin-top:22px">Gruppen</h3><p>{{ my_group_names|join(", ") }}</p>{% endif %}
{% set self_edit = name and name == g.user %}
<h3 style="margin-top:22px">Konto</h3>
{% if self_edit %}<p class="hint">Dein eigenes Konto kannst du nicht deaktivieren oder sperren.</p>{% else %}
<div class="seg"><label><input type="radio" name="active" value="1" {{ "checked" if not u.disabled }}><span>✅ Aktiv</span></label>
<label><input type="radio" name="active" value="0" {{ "checked" if u.disabled }}><span>⛔ Deaktiviert</span></label></div>
{% if u.disabled_by %}<div class="hint fehler">Automatisch deaktiviert wegen {{ u.disabled_by }}. „Aktiv“ wählen und speichern, um es freizugeben.</div>{% endif %}
{% if u.auto_lock_until %}<label class="check"><input type="checkbox" name="unlock"> Zeitsperre nach Fehlversuchen aufheben (bis {{ u.auto_lock_until|dt }})</label>{% endif %}
<label class="check" style="margin-top:12px"><input type="checkbox" name="lock" id="lockchk" {{ "checked" if u.lock_from or u.lock_until }} onchange="document.getElementById('lockbox').style.display=this.checked?'':'none'"> Sperrzeitraum planen</label>
<div id="lockbox" style="{{ '' if u.lock_from or u.lock_until else 'display:none' }}"><div class="row">
<div><label>Gesperrt ab</label><input type="datetime-local" name="lock_from" value="{{ u.lock_from or '' }}"><div class="hint">leer = ab sofort</div></div>
<div><label>Wieder aktiv ab</label><input type="datetime-local" name="lock_until" value="{{ u.lock_until or '' }}"><div class="hint">leer = bleibt gesperrt, bis du es änderst</div></div></div>
<div class="hint">Während der Sperre kann sich der Benutzer nicht anmelden, offene Sitzungen enden sofort. Danach ist das Konto automatisch wieder aktiv. Zeitzone des Containers.</div></div>{% endif %}
{% if name and u.passkeys %}<label class="check"><input type="checkbox" name="reset_passkeys"> Alle {{ u.passkeys|length }} Passkeys dieses Benutzers entfernen (z. B. Gerät verloren)</label>{% endif %}
{% if name and u.totp_enabled %}<label class="check"><input type="checkbox" name="reset_2fa"> 2FA zurücksetzen (z. B. Handy verloren). Der Benutzer meldet sich dann nur mit Passwort an und kann 2FA neu einrichten.</label>{% endif %}
<h3 style="margin-top:22px">Zwei-Faktor-Anmeldung (2FA)</h3><input type="hidden" name="r2fa_form" value="1">
<label class="check"><input type="checkbox" name="require_2fa" {{ "checked" if (form.get('require_2fa') if form.get('r2fa_form') else req_default) }}> 2FA erzwingen</label>
{% if req_all %}<div class="hint">Zurzeit ist 2FA global für alle Benutzer Pflicht (Einstellungen → Allgemein), das Häkchen wirkt erst, wenn du das dort wieder änderst.</div>{% endif %}
<div class="hint">Nach der Anmeldung kann der Benutzer nichts anderes tun, bis er unter „Mein Konto“ eine Authenticator-App eingerichtet hat. Er kann 2FA danach nicht selbst ausschalten.</div>{% if name %}<div class="hint">{% if u.totp_enabled %}2FA ist bei diesem Benutzer eingerichtet.{% else %}2FA ist bei diesem Benutzer noch nicht eingerichtet.{% endif %}</div>{% endif %}
<p style="margin-top:20px"><button class="btn pri">Speichern</button> <a class="btn" href="/users">Abbrechen</a></p>
</form>
{% endblock %}
""",
"account.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}
{% block body %}{% if not welcome and not force_2fa %}{% include "tabs.html" %}{% endif %}
{% if force_2fa %}<div class="card" style="border-color:var(--acc)"><h2>{{ ICON.lock }} Zwei-Faktor-Anmeldung einrichten</h2>
<p class="mut" style="margin:0">Für dein Konto ist eine Zwei-Faktor-Anmeldung Pflicht. Richte sie unten mit einer Authenticator-App ein, danach kannst du MirrorSync wie gewohnt benutzen.</p>
<p style="margin:12px 0 0"><a class="btn sm" href="/logout">Abmelden</a></p></div>{% endif %}
{% if welcome %}<div class="card" style="border-color:var(--acc)"><h2>Schritt 2 von 2: Konto zusätzlich absichern (optional)</h2>
<p class="mut" style="margin:0 0 12px">Dein Admin <b style="color:var(--fg)">{{ g.user }}</b> ist angelegt und angemeldet. Du kannst jetzt eine Zwei-Faktor-Anmeldung und einen Passkey einrichten, beides geht auch später unter Einstellungen → Mein Konto.</p>
<a class="btn pri" href="/account?done=1">Fertig, weiter zur Übersicht</a></div>{% endif %}
{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
{% if codes %}<div class="card" style="border-color:var(--acc)"><h2>Deine Backup-Codes</h2>
<p class="mut">Jeder Code funktioniert genau einmal, falls du keinen Zugriff auf die Authenticator-App hast. <b>Jetzt speichern oder ausdrucken</b>, sie werden nur dieses eine Mal angezeigt.</p>
<div class="codes" id="codes">{% for c in codes %}<span>{{ c }}</span>{% endfor %}</div>
<p><button type="button" class="btn sm" onclick="navigator.clipboard.writeText([...document.querySelectorAll('#codes span')].map(e=>e.textContent).join('\n'));this.textContent='Kopiert'">Kopieren</button>
<button type="button" class="btn sm" onclick="window.print()">Drucken</button></p></div>{% endif %}

{% if not welcome %}<div class="card"><h2>Konto</h2>
<p class="mut" style="margin:0">Angemeldet als <b style="color:var(--fg)">{{ g.user }}</b> · Rolle {{ role_name(g.role) }}</p>
<form method="post" style="margin-top:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap"><input type="hidden" name="action" value="language">
<label for="mylang" style="margin:0">Sprache</label><select id="mylang" name="language" style="width:auto;min-width:180px"><option value="">Standard des Systems</option>{% for c, n in LANGS() %}<option value="{{ c }}" {{ "selected" if c == g.user_lang }}>{{ n }}</option>{% endfor %}</select>
<button class="btn sm">Übernehmen</button></form>
{% if my_logins %}<h3 style="margin-top:24px">Deine letzten Anmeldungen</h3><table><tr><th>Zeit</th><th>IP-Adresse</th><th class="hide-sm">Land</th><th>Ergebnis</th></tr>
{% for e in my_logins %}<tr><td><small>{{ e.time }}</small></td><td><code>{{ e.ip }}</code></td><td class="hide-sm">{{ e.flag }} {{ e.country }}</td>
<td>{% if e.ok %}<span class="tag ok">ok</span>{% else %}<span class="tag fehler">fehlgeschlagen</span>{% endif %} <small class="mut">{{ e.reason }}</small></td></tr>{% endfor %}</table>
<p class="hint">Eine Anmeldung, die du nicht kennst? Sofort das Passwort ändern und 2FA einschalten.</p>{% endif %}</div>{% endif %}

<div class="card"><h2>Passkeys</h2>
<p class="mut" style="margin-top:0">Mit einem Passkey meldest du dich ohne Passwort an: per Fingerabdruck, Gesicht, Geräte-PIN oder Sicherheitsschlüssel (z. B. YubiKey). Der Passkey ersetzt Passwort und 2FA-Code.</p>
{% if passkeys_list %}<table><tr><th>Name</th><th class="hide-sm">Eingerichtet</th><th class="hide-sm">Zuletzt benutzt</th><th style="text-align:right">Aktionen</th></tr>
{% for p in passkeys_list %}<tr><td>🔑 <b>{{ p.name }}</b><br><small class="mut">{{ p.rp_id }}{% if p.synced %} · synchronisiert{% endif %}</small></td><td class="hide-sm"><small>{{ p.created }}</small></td><td class="hide-sm"><small>{{ p.last_used or "noch nie" }}</small></td>
<td style="text-align:right;white-space:nowrap"><details class="pausemenu"><summary class="btn sm">Ändern</summary><div class="pmenu" style="min-width:260px">
<form method="post"><input type="hidden" name="action" value="passkey_rename"><input type="hidden" name="id" value="{{ p.id }}"><label style="margin-top:0">Name</label><div class="row" style="flex-direction:row"><input type="text" name="name" value="{{ p.name }}" maxlength="60"><button class="btn sm" style="flex:0 0 auto">Speichern</button></div></form>
<form method="post" onsubmit="return confirm('Passkey {{ p.name }} entfernen?')"><input type="hidden" name="action" value="passkey_delete"><input type="hidden" name="id" value="{{ p.id }}"><label>Entfernen</label><div class="row" style="flex-direction:row"><input type="password" name="password" placeholder="Passwort zur Bestätigung" required><button class="btn sm del" style="flex:0 0 auto">Entfernen</button></div></form>
</div></details></td></tr>{% endfor %}</table>{% endif %}
<div id="pkadd" style="margin-top:12px">
{% if pk_problem %}<div class="msg info" style="margin:0">{{ pk_problem }}</div>
{% else %}<div class="row" style="flex-direction:row;align-items:flex-end;max-width:560px"><div><label style="margin-top:0">Name für diesen Passkey</label><input type="text" id="pkname" maxlength="60" placeholder="z. B. iPhone, Windows Hello, YubiKey"></div>
<button type="button" class="btn pri" style="flex:0 0 auto" onclick="pkAdd()">🔑 Passkey hinzufügen</button></div>
<div class="hint">Gilt für <code>{{ pk_rp }}</code>. Passkeys sind an diese Adresse gebunden und funktionieren nur über HTTPS.</div>
<div id="pkmsg" class="hint"></div>{% endif %}</div>
<script>
{% raw %}const b64u={dec:s=>Uint8Array.from(atob(s.replace(/-/g,'+').replace(/_/g,'/')+'==='.slice((s.length+3)%4)),c=>c.charCodeAt(0)).buffer,
 enc:b=>btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')};
function pkCredJSON(c){if(c.toJSON)try{return c.toJSON()}catch(e){}const r=c.response,o={id:c.id,rawId:b64u.enc(c.rawId),type:c.type,clientExtensionResults:c.getClientExtensionResults?c.getClientExtensionResults():{},response:{clientDataJSON:b64u.enc(r.clientDataJSON)}};
 if(r.attestationObject)o.response.attestationObject=b64u.enc(r.attestationObject);if(r.getTransports)o.response.transports=r.getTransports();if(c.authenticatorAttachment)o.authenticatorAttachment=c.authenticatorAttachment;return o}
(function(){const box=document.getElementById('pkadd');if(!box||!document.getElementById('pkname'))return;
 if(!window.isSecureContext){box.innerHTML='<div class="msg info" style="margin:0">Passkeys gehen nur über HTTPS. Du hast MirrorSync gerade über <code>'+location.origin.replace(/[<>&]/g,'')+'</code> geöffnet. Öffne es über deine HTTPS-Adresse (z. B. über den Reverse-Proxy), dann kannst du hier einen Passkey einrichten.</div>'}
 else if(!window.PublicKeyCredential){box.innerHTML='<div class="msg info" style="margin:0">Dieser Browser unterstützt keine Passkeys.</div>'}})();
async function pkAdd(){const m=document.getElementById('pkmsg');m.className='hint';m.textContent='Folge den Anweisungen deines Geräts …';
 try{let r=await fetch('/account/passkey/options',{method:'POST',headers:{Accept:'application/json'}});let o=await r.json();if(o.ok===false)throw new Error(o.error);
  o.challenge=b64u.dec(o.challenge);o.user.id=b64u.dec(o.user.id);(o.excludeCredentials||[]).forEach(c=>c.id=b64u.dec(c.id));
  const cred=await navigator.credentials.create({publicKey:o});
  r=await fetch('/account/passkey/register',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({credential:pkCredJSON(cred),name:document.getElementById('pkname').value})});
  const res=await r.json();if(!res.ok)throw new Error(res.error);location.reload()}
 catch(e){m.className='hint fehler';m.textContent=e.name==='InvalidStateError'?'Auf diesem Gerät ist schon ein Passkey für dein Konto gespeichert.':e.name==='NotAllowedError'?'Abgebrochen.':(e.message||String(e))}}{% endraw %}
</script>
</div>

<div class="card"><h2>Zwei-Faktor-Anmeldung (2FA)</h2>
{% if u.totp_enabled %}
<p><span class="tag ok">aktiv</span> &nbsp;<span class="mut">Beim Anmelden wird zusätzlich ein Code aus deiner Authenticator-App abgefragt. Noch {{ backup_left }} Backup-Codes übrig.</span></p>
<div class="row"><form method="post"><input type="hidden" name="action" value="codes"><label>Neue Backup-Codes erzeugen</label>
<div class="row" style="flex-direction:row"><input type="password" name="password" placeholder="Passwort zur Bestätigung" required><button class="btn" style="flex:0 0 auto">Erzeugen</button></div></form>
{% if must_2fa %}<div><label>2FA ausschalten</label><div class="hint">Für dein Konto ist 2FA Pflicht. Ausschalten kann sie nur ein Administrator.</div></div>
{% else %}<form method="post" onsubmit="return confirm('2FA wirklich ausschalten?')"><input type="hidden" name="action" value="2fa_disable"><label>2FA ausschalten</label>
<div class="row" style="flex-direction:row"><input type="password" name="password" placeholder="Passwort zur Bestätigung" required><button class="btn del" style="flex:0 0 auto">Ausschalten</button></div></form>{% endif %}</div>
{% elif setup_secret %}
<div style="display:flex;gap:24px;flex-wrap:wrap;align-items:flex-start">
<div class="qr">{{ qr|safe }}</div>
<div style="flex:1;min-width:240px">
<ol style="margin:0;padding-left:18px;line-height:1.8">
<li>Authenticator-App öffnen (z. B. Google Authenticator, Microsoft Authenticator, Aegis, 2FAS, Bitwarden).</li>
<li>QR-Code scannen. Ohne Kamera diesen Schlüssel eingeben:<br><code style="user-select:all;word-break:break-all">{{ setup_secret }}</code></li>
<li>Den 6-stelligen Code aus der App hier eintragen:</li></ol>
<form method="post" style="margin-top:8px"><input type="hidden" name="action" value="2fa_confirm">
<div class="row" style="flex-direction:row"><input type="text" name="code" inputmode="numeric" autocomplete="one-time-code" placeholder="123456" required autofocus style="max-width:180px;letter-spacing:.2em">
<button class="btn pri" style="flex:0 0 auto">Aktivieren</button></div></form>
</div></div>
{% else %}
<p class="mut">Schützt dein Konto zusätzlich mit einem Code aus einer Authenticator-App. Du bekommst außerdem Backup-Codes für den Notfall.</p>
<form method="post"><input type="hidden" name="action" value="2fa_start"><button class="btn pri">{{ ICON.lock }} 2FA einrichten</button></form>
{% endif %}
</div>

{% if not welcome %}<form method="post" class="card"><h2>Passwort ändern</h2><input type="hidden" name="action" value="password">
<label>Aktuelles Passwort</label><input type="password" name="old" autocomplete="current-password" required>
<div class="row"><div><label>Neues Passwort</label><input type="password" name="password" autocomplete="new-password" required></div>
<div><label>Wiederholen</label><input type="password" name="password2" autocomplete="new-password" required></div></div>
<div class="hint">Mindestens 8 Zeichen. Andere angemeldete Geräte werden abgemeldet.</div>
<p style="margin-top:16px"><button class="btn pri">Passwort ändern</button></p></form>{% endif %}
{% endblock %}
""",
"roles.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}
{% block actions %}<a class="btn pri" href="/roles/new">{{ ICON.plus }} Neue Rolle</a>{% endblock %}
{% block body %}{% include "tabs.html" %}
{% if msg %}<div class="msg info">{{ msg }}</div>{% endif %}
<div class="card" style="padding:6px 8px">
<table><tr><th>Rolle</th><th>Rechte</th><th class="hide-sm">Gilt für</th><th>Benutzer</th><th style="text-align:right">Aktionen</th></tr>
{% for rid, r in roles.items() %}<tr>
<td><b>{{ r.name }}</b>{% if r.locked %} <span class="tag">fest</span>{% elif r.builtin %} <span class="tag">Vorlage</span>{% endif %}<br><small>{{ r.description }}</small></td>
<td><small>{% for gname, n, total in summary[rid] %}{{ gname }} {{ n }}/{{ total }}<br>{% else %}keine{% endfor %}</small></td>
<td class="hide-sm"><small>Aufgaben: {{ "alle" if r.jobs == "all" else (r.jobs|length ~ " ausgewählte") }}<br>Speicherorte: {{ "alle" if r.remotes == "all" else (r.remotes|length ~ " ausgewählte") }}</small></td>
<td>{{ counts.get(rid, 0) }}</td>
<td style="text-align:right;white-space:nowrap">
{% if not r.locked %}<a class="btn sm" href="/roles/{{ rid }}/edit">Bearbeiten</a>{% endif %}
<a class="btn sm" href="/roles/new?from={{ rid }}" title="Neue Rolle mit diesen Rechten als Ausgangspunkt">Als Vorlage</a>
{% if not r.locked and not counts.get(rid) %}<form class="inline" method="post" action="/roles/{{ rid }}/delete" onsubmit="return confirm('Rolle {{ r.name }} löschen?')"><button class="btn sm del">Entfernen</button></form>{% endif %}
</td></tr>{% endfor %}</table></div>
<p class="hint">Die Rolle Admin hat immer alle Rechte und kann nicht geändert werden, damit sich niemand aussperrt. Änderungen an einer Rolle gelten sofort für alle ihre Benutzer.</p>
{% endblock %}
""",
"api_key_edit.html": r"""{% extends "base.html" %}{% block title %}{{ key.name }}{% endblock %}
{% block body %}{% include "tabs.html" %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
<form method="post" class="card"><h2>API-Key bearbeiten</h2>
<p class="mut" style="margin-top:0"><code>msk_{{ kid }}_…</code> · erstellt {{ key.created }} von {{ key.created_by }} · Status: <b>{{ status }}</b></p>
<div class="row"><div><label>Name</label><input type="text" name="name" value="{{ key.name }}" maxlength="60" required></div>
<div><label>Rolle (Rechte)</label><select name="role">{% for rid, r in roles.items() %}<option value="{{ rid }}" {{ "selected" if rid == key.role }}>{{ r.name }}{% if r.description %} – {{ r.description }}{% endif %}</option>{% endfor %}</select></div></div>
<div class="hint">Gilt sofort für alle Anfragen mit diesem Key. Vergeben kannst du nur Rollen, deren Rechte du selbst hast.</div>
<div class="row"><div><label>Gültig bis (optional)</label><input type="date" name="expires" value="{{ key.expires or '' }}"></div>
<div><label>Nur von diesen IP-Adressen (optional)</label><input type="text" name="ips" value="{{ (key.ips or [])|join(', ') }}" placeholder="z. B. 192.168.1.20, 10.0.0.0/24"></div></div>
<div class="row"><div><label>Sprache der API-Antworten</label><select name="lang"><option value="">{{ _("Wie der Benutzer") }}{% if owner %} ({{ owner }}){% endif %}</option>{% for c, n in LANGS() %}<option value="{{ c }}" {{ "selected" if c == key.lang or '' }}>{{ n }}</option>{% endfor %}</select></div><div></div></div>
<div class="hint">Meldungen, Swagger-Beschreibungen und MCP-Tool-Texte. „Wie der Benutzer“ nimmt die Sprache aus dessen Konto (Mein Konto → Sprache), ohne bekannten Benutzer Englisch. Einzelne Anfragen können sie mit <code>?lang=en</code> oder dem Header <code>Accept-Language</code> überschreiben.</div>
{% if can("groups.manage") and all_groups %}<h3 style="margin-top:22px">Gruppen</h3><input type="hidden" name="grp_form" value="1">
<div class="picklist" style="margin:0">{% for gid, x in all_groups %}<label class="check"><input type="checkbox" name="grp" value="{{ gid }}" {{ "checked" if gid in my_groups }} {{ "disabled" if not x.editable }}> {{ x.name }}</label>{% endfor %}</div>
<div class="hint">Der Key bekommt die Rechte und Sichtbarkeit seiner Gruppen zusätzlich zur Rolle.</div>{% endif %}

<h3 style="margin-top:22px">Aktiv oder deaktiviert</h3>
<div class="seg"><label><input type="radio" name="active" value="1" {{ "checked" if not key.disabled }}><span>✅ Aktiv</span></label>
<label><input type="radio" name="active" value="0" {{ "checked" if key.disabled }}><span>⛔ Deaktiviert</span></label></div>
<div class="hint">Ein deaktivierter Key wird abgelehnt, bleibt aber erhalten und lässt sich jederzeit wieder aktivieren.</div>
<label class="check" style="margin-top:12px"><input type="checkbox" name="lock" id="klock" {{ "checked" if key.lock_from or key.lock_until }} onchange="document.getElementById('klockbox').style.display=this.checked?'':'none'"> Pause planen (Zeitraum)</label>
<div id="klockbox" style="{{ '' if key.lock_from or key.lock_until else 'display:none' }}"><div class="row">
<div><label>Pausiert ab</label><input type="datetime-local" name="lock_from" value="{{ key.lock_from or '' }}"><div class="hint">leer = ab sofort</div></div>
<div><label>Wieder aktiv ab</label><input type="datetime-local" name="lock_until" value="{{ key.lock_until or '' }}"><div class="hint">leer = bis du es änderst</div></div></div></div>
<label class="check" style="margin-top:12px"><input type="checkbox" name="win_on" id="kwin" {{ "checked" if key.windows }} onchange="document.getElementById('kwinbox').style.display=this.checked?'':'none'"> Nur zu bestimmten Zeiten aktiv (wöchentlich)</label>
<div id="kwinbox" style="{{ '' if key.windows else 'display:none' }}">
{% for i in range(4) %}{% set w = key.windows[i] if key.windows and key.windows|length > i else {} %}
<div class="row" style="align-items:flex-end;margin-top:6px"><div style="flex:2"><label>Zeitfenster {{ i + 1 }}</label><div class="days">{% for d in range(7) %}<label><input type="checkbox" name="w{{ i }}_d" value="{{ d }}" {{ "checked" if d in (w.days or []) }}><span>{{ ["Mo","Di","Mi","Do","Fr","Sa","So"][d] }}</span></label>{% endfor %}</div></div>
<div><label>von</label><input type="time" name="w{{ i }}_s" value="{{ w.start or '' }}"></div><div><label>bis</label><input type="time" name="w{{ i }}_e" value="{{ w.end or '' }}"></div></div>{% endfor %}
<div class="hint">Außerhalb dieser Zeiten wird der Key abgelehnt. Leere Zeilen werden ignoriert. Ende vor Beginn (z. B. 22:00–06:00) geht über Mitternacht. Zeitzone des Containers.</div></div>
<p style="margin-top:20px"><button class="btn pri">Speichern</button> <a class="btn" href="/settings/api">Abbrechen</a></p>
</form>
<style>.days{display:flex;gap:4px;flex-wrap:wrap}.days label{display:inline-flex}.days input{display:none}.days span{padding:5px 9px;border:1px solid var(--bd);border-radius:8px;cursor:pointer;font-size:13px}.days input:checked+span{background:var(--acc);color:#fff;border-color:var(--acc)}</style>
{% endblock %}
""",

"groups.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}
{% block actions %}<a class="btn pri" href="/groups/new">{{ ICON.plus }} Neue Gruppe</a>{% endblock %}
{% block body %}{% include "tabs.html" %}
{% if msg %}<div class="msg info">{{ msg }}</div>{% endif %}
{% if not rows %}<div class="card empty"><p>Noch keine Gruppen.</p><p class="hint">Eine Gruppe fasst Benutzer und API-Keys zusammen. Sie kann zusätzliche Rechte geben, und bei jeder Aufgabe und jedem Speicherort lässt sich einstellen, welche Gruppen ihn sehen.</p></div>{% else %}
<div class="card" style="padding:6px 8px">
<table><tr><th>Gruppe</th><th>Mitglieder</th><th class="hide-sm">Zusätzliche Rechte</th><th class="hide-sm">Sieht</th><th style="text-align:right">Aktionen</th></tr>
{% for r in rows %}<tr>
<td><b>{{ r.name }}</b><br><small>{{ r.description }}</small></td>
<td><small>{{ r.members|join(", ") or "–" }}{% if r.key_names %}<br>API: {{ r.key_names|join(", ") }}{% endif %}</small></td>
<td class="hide-sm"><small>{{ r.n_perms if r.n_perms else "keine" }}</small></td>
<td class="hide-sm"><small>{% if r.view_jobs or r.view_remotes %}{% if r.view_jobs %}Aufgaben: {{ r.view_jobs|map(attribute=0)|join(", ") }}<br>{% endif %}{% if r.view_remotes %}Speicherorte: {{ r.view_remotes|join(", ") }}{% endif %}{% else %}nur, was für alle sichtbar ist{% endif %}</small></td>
<td style="text-align:right;white-space:nowrap">{% if r.editable %}<a class="btn sm" href="/groups/{{ r.id }}/edit">Bearbeiten</a>
<form class="inline" method="post" action="/groups/{{ r.id }}/delete" data-q="{{ _('Gruppe „{0}“ löschen? Die Mitglieder behalten ihre Konten, verlieren aber die Rechte und Sichtbarkeit dieser Gruppe.', r.name) }}" onsubmit="return confirm(this.dataset.q)"><button class="btn sm del">Entfernen</button></form>{% else %}<small class="mut">mehr Rechte als du</small>{% endif %}</td></tr>{% endfor %}</table></div>{% endif %}
<p class="hint">Rechte eines Mitglieds = Rechte seiner Rolle plus die Rechte aller seiner Gruppen. Welche Aufgaben und Speicherorte jemand sieht, stellst du bei der Aufgabe bzw. beim Speicherort unter „Sichtbar für“ ein. Admins sehen immer alles.</p>
{% endblock %}
""",

"group_edit.html": r"""{% extends "base.html" %}{% block title %}{{ grp.name if gid else "Neue Gruppe" }}{% endblock %}
{% block body %}{% include "tabs.html" %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
<form method="post">
<div class="card"><h2>Gruppe</h2>
<div class="row"><div><label>Name</label><input type="text" name="name" value="{{ grp.name }}" required maxlength="40"></div>
<div style="flex:2"><label>Beschreibung</label><input type="text" name="description" value="{{ grp.description or '' }}" maxlength="200" placeholder="z. B. Team Buchhaltung"></div></div></div>
<div class="card"><h2>Mitglieder</h2><div class="row">
<div><h3>Benutzer</h3><div class="picklist" style="margin-left:0">{% for n in all_users %}<label class="check"><input type="checkbox" name="member" value="{{ n }}" {{ "checked" if n in grp.members }}> {{ n }}</label>{% endfor %}</div></div>
<div><h3>API-Keys</h3><div class="picklist" style="margin-left:0">{% for k, kname, st in keys if st != "widerrufen" or k in (grp.get('keys') or []) %}<label class="check"><input type="checkbox" name="key" value="{{ k }}" {{ "checked" if k in (grp.get('keys') or []) }}> {{ kname }}{% if st != "aktiv" %} <small class="mut">({{ st }})</small>{% endif %}</label>{% else %}<div class="hint">Noch keine API-Keys.</div>{% endfor %}</div>
<div class="hint">Ein API-Key in einer Gruppe bekommt deren Rechte und Sichtbarkeit zusätzlich zu seiner Rolle.</div></div>
</div></div>
<div class="card"><h2>Zusätzliche Rechte</h2>
<p class="hint" style="margin-top:0">Kommen zu den Rechten der Rolle jedes Mitglieds dazu. Vergeben kannst du nur Rechte, die du selbst hast. Leer lassen, wenn die Gruppe nur für „Sichtbar für“ gedacht ist.</p>
<div class="permgrid">
{% for gname, perms in groups %}<div class="permgroup"><h3>{{ gname }}</h3>
{% for p, label in perms %}<label class="check"><input type="checkbox" name="perm" value="{{ p }}" {{ "checked" if p in grp.perms }} {{ "disabled" if not can(p) and p not in grp.perms }}> {{ label }}</label>{% endfor %}
</div>{% endfor %}
</div></div>
{% if gid %}<div class="card"><h2>Sieht</h2>
{% if view_jobs or view_remotes %}{% if view_jobs %}<p>Aufgaben: {% for n, jid in view_jobs %}<a href="/job/{{ jid }}">{{ n }}</a>{{ ", " if not loop.last }}{% endfor %}</p>{% endif %}
{% if view_remotes %}<p>Speicherorte: {% for n in view_remotes %}<a href="/remotes/{{ n }}/edit">{{ n }}</a>{{ ", " if not loop.last }}{% endfor %}</p>{% endif %}
{% else %}<p class="mut">Noch keine eingeschränkten Aufgaben oder Speicherorte für diese Gruppe.</p>{% endif %}
<div class="hint">Einstellen bei der Aufgabe bzw. beim Speicherort unter „Sichtbar für“. Alles, was dort auf „alle mit Recht“ steht, sehen die Mitglieder ohnehin, wenn ihre Rechte es erlauben.</div></div>{% endif %}
<div><button class="btn pri">Speichern</button> <a class="btn" href="/groups">Abbrechen</a></div>
</form>
<style>.permgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.permgroup{border:1px solid var(--bd);border-radius:10px;padding:12px 14px;background:var(--card2)}
.permgroup h3{margin:0}.picklist{margin:6px 0 0 24px;max-height:260px;overflow:auto}@media(max-width:860px){.permgrid{grid-template-columns:1fr}}</style>
{% endblock %}
""",

"vis_picker.html": r"""{# erwartet: vis ("all" oder Liste), vis_opts, vis_what #}
{% if vis_nocard %}<div style="margin-top:20px"><h3>Sichtbar für</h3>{% else %}<div class="card"><h2>Sichtbar für</h2>{% endif %}
<label class="check"><input type="radio" name="vis_mode" value="all" {{ "checked" if vis is none or vis == "all" }} onchange="visShow()"> alle mit dem passenden Recht</label>
<label class="check"><input type="radio" name="vis_mode" value="some" {{ "checked" if vis is not none and vis != "all" }} onchange="visShow()"> nur ausgewählte Benutzer und Gruppen</label>
<div id="vis_box" class="row" style="margin:6px 0 0 24px">
<div><h3>Gruppen</h3>{% for k, n in vis_opts.groups %}<label class="check"><input type="checkbox" name="vis" value="{{ k }}" {{ "checked" if vis is not none and vis != "all" and k in vis }}> {{ n }}</label>{% else %}<div class="hint">Noch keine Gruppen. Anlegen unter Einstellungen → Gruppen.</div>{% endfor %}</div>
<div><h3>Benutzer</h3>{% for k, n in vis_opts.users %}<label class="check"><input type="checkbox" name="vis" value="{{ k }}" {{ "checked" if vis is not none and vis != "all" and k in vis }}> {{ n }}</label>{% endfor %}</div></div>
<div class="hint">Admins sehen immer alles{% if vis_what == "job" %}, wer die Aufgabe angelegt hat, sieht sie auch{% endif %}. Wer etwas nicht sieht, kann es auch nicht starten, ändern oder als {{ "Auslöser" if vis_what == "job" else "Quelle oder Ziel" }} wählen. Die Rolle kann zusätzlich auf einzelne Aufgaben und Speicherorte beschränken.</div>
<script>function visShow(){document.getElementById('vis_box').style.display=document.querySelector('input[name=vis_mode][value=some]').checked?'':'none'}visShow();</script>
</div>
""",

"role_edit.html": r"""{% extends "base.html" %}{% block title %}{{ role.name if rid else "Neue Rolle" }}{% endblock %}
{% block body %}{% include "tabs.html" %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
{% if locked %}<div class="msg info">Die Rolle Admin hat immer alle Rechte und ist nicht änderbar. Nutze „Als Vorlage“ für eine eigene Variante.</div>{% endif %}
<form method="post"><fieldset {{ "disabled" if locked }}>
<div class="card"><h2>Rolle</h2>
<div class="row"><div><label>Name</label><input type="text" name="name" value="{{ role.name }}" required maxlength="40"></div>
<div style="flex:2"><label>Beschreibung</label><input type="text" name="description" value="{{ role.description }}" maxlength="200" placeholder="wofür ist die Rolle gedacht?"></div></div>
{% if not rid %}<label>Vorlage</label><select onchange="if(this.value)location='/roles/new?from='+this.value"><option value="">– Rechte von einer Rolle übernehmen –</option>
{% for tid, t in templates.items() %}<option value="{{ tid }}">{{ t.name }}</option>{% endfor %}</select>{% endif %}
</div>

<div class="card"><h2>Rechte</h2>
<p class="hint" style="margin-top:0">Wer etwas ändern darf, darf es automatisch auch ansehen.</p>
<div class="permgrid">
{% for gname, perms in groups %}<div class="permgroup">
<div style="display:flex;justify-content:space-between;align-items:center"><h3>{{ gname }}</h3>
<span><button type="button" class="btn sm" onclick="grp(this,true)">alle</button> <button type="button" class="btn sm" onclick="grp(this,false)">keine</button></span></div>
{% for p, label in perms %}<label class="check"><input type="checkbox" name="perm" value="{{ p }}" {{ "checked" if p in role.perms }}> {{ label }}</label>{% endfor %}
</div>{% endfor %}
</div></div>

<div class="card"><h2>Gilt für</h2>
<div class="row">
<div><h3>Aufgaben</h3>
<label class="check"><input type="radio" name="jobs_scope" value="all" {{ "checked" if role.jobs == "all" }} onchange="scope()"> alle Aufgaben</label>
<label class="check"><input type="radio" name="jobs_scope" value="some" {{ "checked" if role.jobs != "all" }} onchange="scope()"> nur ausgewählte Aufgaben</label>
<div id="jobs_list" class="picklist">{% for jid, jname in jobs %}<label class="check"><input type="checkbox" name="job" value="{{ jid }}" {{ "checked" if role.jobs != "all" and jid in role.jobs }}> {{ jname }}</label>{% else %}<div class="hint">Noch keine Aufgaben.</div>{% endfor %}
<div class="hint">Aufgaben, die ein Benutzer selbst anlegt, sieht er immer.</div></div></div>
<div><h3>Speicherorte</h3>
<label class="check"><input type="radio" name="remotes_scope" value="all" {{ "checked" if role.remotes == "all" }} onchange="scope()"> alle Speicherorte</label>
<label class="check"><input type="radio" name="remotes_scope" value="some" {{ "checked" if role.remotes != "all" }} onchange="scope()"> nur ausgewählte Speicherorte</label>
<div id="remotes_list" class="picklist">{% for r in remotes %}<label class="check"><input type="checkbox" name="remote" value="{{ r.name }}" {{ "checked" if role.remotes != "all" and r.name in role.remotes }}> {{ r.name }} <small class="mut">({{ r.type }})</small></label>{% else %}<div class="hint">Noch keine Speicherorte.</div>{% endfor %}
<div class="hint">Gilt für Anzeige, Testen, Durchsuchen und für Quelle/Ziel beim Anlegen und Bearbeiten von Aufgaben.</div></div></div>
</div></div>
</fieldset>
<div>{% if not locked %}<button class="btn pri">Speichern</button> {% endif %}<a class="btn" href="/roles">{{ "Zurück" if locked else "Abbrechen" }}</a></div>
</form>
<style>.permgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.permgroup{border:1px solid var(--bd);border-radius:10px;padding:12px 14px;background:var(--card2)}
.permgroup h3{margin:0}.picklist{margin:6px 0 0 24px}@media(max-width:860px){.permgrid{grid-template-columns:1fr}}</style>
<script>
function grp(b,on){b.closest('.permgroup').querySelectorAll('input[type=checkbox]').forEach(i=>i.checked=on)}
function scope(){for(const k of ['jobs','remotes']){const some=document.querySelector('input[name='+k+'_scope][value=some]').checked;document.getElementById(k+'_list').style.display=some?'':'none'}}
scope();
</script>
{% endblock %}
""",
"run.html": r"""{% extends "base.html" %}{% block title %}{{ job.name }} · Lauf {{ entry.start if entry else run_id }}{% endblock %}{% block subtitle %}<p class="path">{{ job.source }} {{ "⇄" if job.direction == "bisync" else "→" }} {{ job.dest }}</p>{% endblock %}{% block body %}
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
<h2 style="margin:0">Lauf {{ entry.start if entry else run_id }}
{% if live %}<span class="tag laeuft">läuft</span>{% elif entry %}<span class="tag {{ entry.status }}">{{ STATUS.get(entry.status, entry.status) }}</span>{% if entry.dry_run %} <small>Testlauf</small>{% endif %}{% endif %}</h2>
<div><a class="btn" href="/job/{{ job_id }}/run/{{ run_id }}/download">↓ Herunterladen</a> <a class="btn" href="/job/{{ job_id }}/log">Zurück</a></div></div>
{% if entry %}<p class="mut" style="margin:8px 0 0">Dauer {{ entry.duration }} s · gestartet von {{ entry.by or "–" }}{% if entry.code is defined %} · Rückgabewert {{ entry.code }}{% endif %}</p>{% endif %}

<form method="get" style="margin-top:14px">
<div class="chips">{% for k, label in filters.items() %}<a class="chip {{ 'active' if flt == k }}" href="?f={{ k }}{% if q %}&q={{ q|urlencode }}{% endif %}">{{ label }} <b>{{ counts[k] }}</b></a>{% endfor %}</div>
<div class="row" style="align-items:flex-end"><div style="flex:4"><input type="text" name="q" value="{{ q }}" placeholder="Im Log suchen, z. B. Dateiname oder Ordner"></div>
<input type="hidden" name="f" value="{{ flt }}">
<div style="flex:0 0 auto"><button class="btn">Suchen</button>{% if q %} <a class="btn" href="?f={{ flt }}">Zurücksetzen</a>{% endif %}</div></div>
</form>
<p class="hint">{{ total }} {{ "Zeile" if total == 1 else "Zeilen" }}{% if flt != "all" or q %} gefunden{% endif %}{% if total > max_lines %}, angezeigt werden die letzten {{ max_lines }}. Das ganze Log bekommst du über „Herunterladen“{% endif %}.{% if live %} Die Seite aktualisiert sich alle 3 Sekunden.{% endif %}</p>
{% if lines %}<pre id="log" class="lines">{% for kind, line in lines %}<span class="{{ kind }}">{{ line }}</span>{% endfor %}</pre>
{% else %}<div class="empty">Keine passenden Zeilen.</div>{% endif %}
</div>
<script>const l=document.getElementById('log');if(l&&{{ 'true' if live else 'false' }})l.scrollTop=l.scrollHeight</script>
{% endblock %}""",
"general.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}{% block body %}{% include "tabs.html" %}
{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
<form method="post" class="card"><input type="hidden" name="section" value="lang"><h2>Sprache</h2>
<div class="row"><div><label>Standardsprache</label><select name="language">{% for c, n in LANGS() %}<option value="{{ c }}" {{ "selected" if c == s.language }}>{{ n }}</option>{% endfor %}</select></div>
<div style="align-self:end"><button class="btn pri">Speichern</button></div></div>
<div class="hint">Gilt für die Anmeldeseite, Benachrichtigungen, API-Meldungen und alle Benutzer ohne eigene Auswahl. Jeder Benutzer stellt seine Sprache unter <a href="/account">Mein Konto</a> ein.</div></form>
<form method="post" class="card"><input type="hidden" name="section" value="files"><h2>Dateimanager</h2>
<div class="row"><div style="flex:0 0 300px"><label for="files_speed">Tempo beim Kopieren und Verschieben</label><select name="files_speed" id="files_speed">
{% set fsp = s.files_speed or "normal" %}<option value="gentle" {{ "selected" if fsp == "gentle" }}>Schonend (2 parallel)</option>
<option value="normal" {{ "selected" if fsp == "normal" }}>Normal (4 parallel)</option>
<option value="fast" {{ "selected" if fsp == "fast" }}>Schnell (8 parallel)</option>
<option value="max" {{ "selected" if fsp == "max" }}>Sehr schnell (16 parallel)</option></select></div>
<div style="align-self:end"><button class="btn pri">Speichern</button></div></div>
<div class="hint">Wie viele Dateien der Dateimanager gleichzeitig überträgt. Mehr parallel lohnt sich vor allem bei vielen kleinen Dateien und bei Clouds. Aufgaben haben ihr eigenes Tempo unter „Optionen“.</div></form>
<form method="post" class="card"><input type="hidden" name="section" value="update"><h2>Updates</h2>
<label class="check"><input type="checkbox" name="update_check" {{ "checked" if upd.enabled }}> Nach neuen Versionen suchen</label>
{% set upd_h = upd.interval_minutes % 60 == 0 %}<div class="row" style="margin-top:8px"><div style="flex:0 0 300px"><label>Prüfen alle</label><div style="display:flex;gap:8px"><input type="number" name="update_interval_value" min="1" max="43200" value="{{ (upd.interval_minutes // 60) if upd_h else upd.interval_minutes }}" style="width:110px"><select name="update_interval_unit"><option value="min" {{ "selected" if not upd_h }}>Minuten</option><option value="h" {{ "selected" if upd_h }}>Stunden</option></select></div></div></div>
<div class="hint">Fragt im eingestellten Abstand bei GitHub nach, ob es eine neuere Version gibt, und zeigt sie unten links neben der Versionsnummer an. Übertragen wird dabei nur die eigene Versionsnummer. Erlaubt sind 5 Minuten bis 720 Stunden, Standard 1 Stunde.</div>
<label class="check" style="margin-top:12px"><input type="checkbox" name="update_notify" {{ "checked" if upd.notify }}> Benachrichtigung schicken, wenn eine neue Version verfügbar ist</label>
<div style="display:flex;gap:14px;flex-wrap:wrap;padding:4px 0 0 26px"><span class="mut">Kanäle:</span>{% for c, n, on in upd_channels %}<label class="check" style="margin:0"><input type="checkbox" name="update_ch_{{ c }}" {{ "checked" if c in upd.notify_channels }}> {{ n }}{% if not on %} <small class="mut">(global aus)</small>{% endif %}</label>{% endfor %}</div>
<div class="hint" style="margin-left:26px">Je neue Version kommt genau eine Nachricht. Kein Kanal angehakt = alle eingeschalteten Kanäle. Den Text kannst du unter Benachrichtigungen → Texte der Benachrichtigungen anpassen („Neue MirrorSync-Version verfügbar“).</div>
<p style="margin:10px 0 0"><span class="mut">Installiert:</span> <b>v{{ upd.current }}</b>{% if upd.latest %} &nbsp;·&nbsp; <span class="mut">Neueste Version:</span> <a href="{{ upd.url }}" target="_blank" rel="noopener">v{{ upd.latest }}</a>{% if upd.update_available %} <span class="tag ok">Neue Version verfügbar</span>{% elif upd.enabled %} <span class="tag">aktuell</span>{% endif %}{% endif %}</p>
{% if upd.checked %}<p class="mut" style="margin:4px 0 0"><small>Zuletzt geprüft: {{ upd.checked }}</small></p>{% endif %}
{% if upd.error %}<p style="margin:4px 0 0;color:var(--err)"><small>Fehler bei der letzten Prüfung: {{ upd.error }}</small></p>{% endif %}
<p style="margin-top:12px"><button class="btn pri">Speichern</button> <button class="btn" name="check_only" value="1" formnovalidate>Jetzt prüfen</button></p></form>
{% if selfupd %}{% set su = selfupd %}{% set sst = su.state or {} %}<div class="card" id="selfupdate"><h2>Selbst aktualisieren</h2>
{% if not su.available %}<p class="mut" style="margin-top:-4px">Ausgeschaltet. MirrorSync kann sich selbst aktualisieren, wenn der Docker-Socket in den Container eingebunden ist (in der Compose-Datei unter <code>volumes:</code> die Zeile <code>- /var/run/docker.sock:/var/run/docker.sock</code>). Achtung: Wer den Socket hat, hat volle Kontrolle über alle Container auf dem Host. Ohne Socket aktualisierst du wie bisher über Dockhand, Portainer oder <code>docker compose pull &amp;&amp; docker compose up -d</code>.</p>{% if su.reason and su.reason != "socket" %}<p class="hint fehler"><span>Socket gefunden, aber Docker antwortet nicht:</span> <code>{{ su.reason }}</code></p>{% endif %}
{% else %}<p class="mut" style="margin-top:-4px">Holt das Image neu und legt den Container mit genau denselben Einstellungen neu an (Name, Ports, Volumes, Umgebungsvariablen, Netzwerke mit fester IP, Neustart-Regel, Labels von Docker Compose). Startet die neue Version nicht, läuft automatisch wieder die bisherige.</p>
<p class="hint"><span>Container:</span> <b>{{ su.container }}</b> · <span>Image:</span> <code>{{ su.image }}</code>{% if su.compose_project %} · <span>Compose-Projekt:</span> <code>{{ su.compose_project }}</code>{% endif %}</p>
{% if su.local_only %}<p class="hint fehler">Das Image wurde lokal gebaut (<code>build: .</code>) und liegt in keinem Registry, daher kann MirrorSync kein neues holen. Für Selbst-Updates in der Compose-Datei <code>image: ghcr.io/dermilderjoghurt/mirrorsync:latest</code> verwenden und <code>build: .</code> entfernen.</p>
{% elif su.pinned %}<p class="hint">Hinweis: Das Image hat einen festen Versions-Tag. Aktualisieren holt nur diesen Tag neu. Für neue Versionen <code>:latest</code> verwenden.</p>{% endif %}
{% if sst.state in ("pulling", "running") %}<div class="msg info"><span>Update läuft seit</span> {{ sst.started }} …{% if sst.log %} <small>{{ sst.log[-1] }}</small>{% endif %}</div>
{% elif sst.state == "ok" %}<p><span class="tag ok">Letztes Update erfolgreich</span> <small class="mut">v{{ sst.from_version }} → v{{ sst.to_version }}, {{ sst.finished }}</small></p>
{% elif sst.state in ("failed", "error") %}<p><span class="tag fehler">Letztes Update fehlgeschlagen</span> <small class="mut">{{ sst.finished }}: {{ sst.error }}</small></p>
{% elif sst.state == "current" %}<p><span class="tag">aktuell</span> <small class="mut"><span>Zuletzt geprüft</span> {{ sst.checked }}</small></p>{% endif %}
{% if can("system.update") %}<form method="post" action="/update/apply" onsubmit="return confirm('MirrorSync jetzt aktualisieren? Ist ein neueres Image da, wird der Container neu gestartet und die Oberfläche ist etwa eine Minute nicht erreichbar.')"><input type="hidden" name="back" value="/settings/general#selfupdate"><button class="btn pri" {{ "disabled" if su.local_only }}>Jetzt aktualisieren</button>{% if su.jobs_running %} <small class="mut">Es laufen gerade Aufgaben, das Update ist erst danach möglich.</small>{% endif %}</form>{% endif %}
<form method="post" style="margin-top:16px"><input type="hidden" name="section" value="selfupdate">
<label class="check"><input type="checkbox" name="selfupdate_auto" {{ "checked" if su.auto }}> Automatisch aktualisieren, einmal am Tag</label>
<div class="row"><div style="flex:0 0 200px"><label>Ab Uhrzeit</label><input type="time" name="selfupdate_time" value="{{ su.time }}"></div></div>
<label class="check"><input type="checkbox" name="selfupdate_prune" {{ "checked" if s.selfupdate_prune is not defined or s.selfupdate_prune }}> Altes Image nach dem Update löschen</label>
<div class="hint">Läuft gerade eine Aufgabe, wartet das Update, bis sie fertig ist. Zeitzone des Containers. Das alte Image wird nur gelöscht, wenn es kein anderer Container mehr verwendet.</div>
<p><button class="btn pri">Speichern</button></p></form>
{% if old_imgs is not none %}<h3 style="margin-top:18px">Alte MirrorSync-Images</h3>
{% if old_imgs %}<table><tr><th>Version</th><th>Image-Tag</th><th>Erstellt</th><th>Größe</th></tr>{% for im in old_imgs %}<tr><td>{{ "v" ~ im.version if im.version else "–" }}</td><td><code>{{ im.tags|join(", ") or im.id[7:19] }}</code></td><td>{{ im.created }}</td><td>{{ (im.size / 1048576)|round|int }} MB</td></tr>{% endfor %}</table>
{% if can("system.update") %}<form method="post" action="/system/images/prune" onsubmit="return confirm('Die alten MirrorSync-Images löschen? Ein Zurückspringen auf diese Versionen braucht danach wieder einen Download.')" style="margin-top:10px"><input type="hidden" name="back" value="/settings/general#selfupdate"><button class="btn del">Alte Images entfernen</button></form>{% endif %}
{% else %}<p class="mut">Keine alten Images vorhanden.</p>{% endif %}{% endif %}{% endif %}</div>{% endif %}
{% if restart %}{% set rs = restart %}<div class="card" id="restart"><h2>Neustart</h2>
<p class="mut" style="margin-top:-4px">Startet den Container von MirrorSync neu, zum Beispiel wenn eine Verbindung hängt. Die Oberfläche ist danach einige Sekunden nicht erreichbar. Laufende Aufgaben werden dabei abgebrochen.</p>
{% if rs.socket %}<p class="hint"><span>Weg:</span> <b><span>Docker-Socket</span></b> · <span>Neustart-Regel:</span> <code>{{ rs.policy or "?" }}</code></p>
{% else %}<p class="hint">Ohne Docker-Socket beendet sich MirrorSync und Docker startet den Container über die Neustart-Regel wieder. Dafür muss in der Compose-Datei <code>restart: unless-stopped</code> (oder <code>always</code>) stehen, sonst bleibt MirrorSync aus.</p>{% endif %}
{% if rs.socket and rs.policy in ("no", "") %}<p class="hint fehler"><span>Achtung: Die Neustart-Regel des Containers ist</span> <code>{{ rs.policy or "no" }}</code>. <span>Der Neustart klappt über den Socket trotzdem, aber nach einem Neustart des Hosts startet MirrorSync nicht von selbst.</span></p>{% endif %}
{% if rs.last and rs.last.done %}<p><span class="tag ok">Letzter Neustart</span> <small class="mut">{{ rs.last.done }} · {{ rs.last.by }}</small></p>{% endif %}
{% if can("system.restart") %}<form method="post" action="/system/restart" onsubmit="return confirm('MirrorSync jetzt neu starten? Die Oberfläche ist einige Sekunden nicht erreichbar.')"><input type="hidden" name="back" value="/settings/general#restart"><button class="btn pri">Jetzt neu starten</button>{% if rs.jobs_running %} <label class="check" style="display:inline-flex;margin-left:10px"><input type="checkbox" name="force" value="1"> <span>auch wenn Aufgaben laufen</span> ({{ rs.jobs_running|length }})</label>{% endif %}</form>{% endif %}
<form method="post" style="margin-top:16px"><input type="hidden" name="section" value="restart">
<label class="check"><input type="checkbox" name="restart_auto" {{ "checked" if rs.auto }}> Nach Zeitplan neu starten</label>
<div class="row"><div style="flex:0 0 200px"><label>Uhrzeit</label><input type="time" name="restart_time" value="{{ rs.time }}"></div>
<div><label>Wochentage</label><div style="display:flex;gap:10px;flex-wrap:wrap">{% for d in range(7) %}<label class="check" style="margin:0"><input type="checkbox" name="restart_day_{{ d }}" {{ "checked" if d in rs.days }}> {{ day_names[d] }}</label>{% endfor %}</div></div></div>
<div class="hint">Läuft gerade eine Aufgabe, wartet der Neustart, bis sie fertig ist (höchstens bis Mitternacht). Zeitzone des Containers.</div>
<p><button class="btn pri">Speichern</button></p></form></div>{% endif %}
<form method="post" class="card" id="monitor"><input type="hidden" name="section" value="monitor"><h2>Überwachung und Datenvolumen</h2>
<p class="mut" style="margin-top:-4px">Für Uptime Kuma, Home Assistant, Grafana und andere: Zustand der Aufgaben und Kennzahlen abrufen.</p>
<table class="chg" style="margin:6px 0 8px"><tr><td><b>Health</b></td><td><code>{{ base_url }}/health/jobs</code></td></tr>
<tr><td></td><td><small class="mut">HTTP 200 = alles in Ordnung, 503 = Fehler, überfällig oder Löschwarnung. Eine Aufgabe: <code>/health/jobs/&lt;ID oder Name&gt;</code>, als Text: <code>?format=text</code> („OK: 3 Aufgaben ok, letzter Sync vor 5 Minuten“).</small></td></tr>
<tr><td><b>Prometheus</b></td><td><code>{{ base_url }}/metrics</code></td></tr>
<tr><td></td><td><small class="mut">Läufe, Datenmengen, Dauer, Zustand und freier Speicher je Aufgabe, für Grafana.</small></td></tr></table>
<div class="hint">Zugriff mit einem API-Key mit dem Recht <code>system.monitor</code> (oder <code>jobs.view</code>): Header <code>Authorization: Bearer msk_…</code> oder <code>?key=msk_…</code> in der Adresse. Es erscheinen nur die Aufgaben, die der Key sehen darf.</div>
<label class="check"><input type="checkbox" name="monitor_public" {{ "checked" if s.monitor_public }}> Ohne Anmeldung abrufbar (zeigt Namen und Zustand aller Aufgaben, keine Pfade oder Zugangsdaten)</label>
<div class="section"><h3>Datenvolumen pro Monat</h3>
<div class="row"><div style="flex:0 0 220px"><label>Limit (GB pro Monat)</label><input type="text" inputmode="decimal" name="volume_limit_gb" value="{{ s.volume_limit_gb or '' }}" placeholder="kein Limit"></div>
<div style="flex:0 0 200px"><label>Warnen ab (%)</label><input type="text" inputmode="numeric" name="volume_warn_pct" value="{{ s.volume_warn_pct or '80' }}"></div>
<div>{% if vol %}<label>Dieser Monat</label><div style="margin-top:8px"><b>{{ vol.used|hbytes }}</b> von {{ vol.limit|hbytes }} ({{ vol.pct }} %)</div><div class="fm-bar" style="width:100%;margin-top:6px"><i style="width:{{ [vol.pct,100]|min }}%;background:{{ 'var(--err)' if vol.exceeded else ('var(--warn)' if vol.warn else 'var(--ok)') }}"></i></div>{% endif %}</div></div>
<label class="check"><input type="checkbox" name="volume_notify" {{ "checked" if s.volume_notify is not false }}> Benachrichtigen, wenn die Warnschwelle und wenn das Limit erreicht ist</label>
<label class="check"><input type="checkbox" name="volume_stop" {{ "checked" if s.volume_stop }}> Bei erreichtem Limit automatische Läufe bis zum Monatsende anhalten (von Hand gestartete laufen weiter)</label>
<div class="hint">Gezählt wird, was MirrorSync in echten Läufen überträgt. Den Verlauf je Monat und Aufgabe zeigt die Seite <a href="/stats">Statistik</a>.</div></div>
<p><button class="btn pri">Speichern</button></p></form>
<form method="post"><div class="card"><h2>Logs aufbewahren</h2>
<p class="mut" style="margin-top:-4px">Jeder Lauf bekommt ein eigenes Log. Ältere Läufe werden nach jedem Lauf automatisch gelöscht.</p>
<div class="row"><div><label>Läufe pro Aufgabe behalten</label><input type="text" inputmode="numeric" name="log_keep_runs" value="{{ s.log_keep_runs }}"><div class="hint">0 bis 1000, 0 = unbegrenzt</div></div>
{% set ku = s.log_keep_unit if s.log_keep_unit in ("d", "w", "m") else "d" %}{% set kf = {"d": 1, "w": 7, "m": 30}[ku] %}<div><label>Höchstens so lange behalten</label><div style="display:flex;gap:8px"><input type="text" inputmode="numeric" name="log_keep_value" value="{{ ((s.log_keep_days or 0)|int // kf) }}" style="width:110px"><select name="log_keep_unit"><option value="d" {{ "selected" if ku == "d" }}>Tage</option><option value="w" {{ "selected" if ku == "w" }}>Wochen</option><option value="m" {{ "selected" if ku == "m" }}>Monate</option></select></div><div class="hint">0 = unbegrenzt. Ein Monat zählt als 30 Tage.</div></div></div>
<div class="row"><div><label>Audit-Log: so viele Tage behalten</label><input type="text" inputmode="numeric" name="audit_keep_days" value="{{ s.audit_keep_days }}"><div class="hint">0 = unbegrenzt (höchstens die neuesten 20 000 Einträge).</div></div><div></div></div>
<p class="hint">Belegt zurzeit: {{ "%.1f"|format(usage / 1048576) }} MB in <code>/logs</code>.</p>
<p><button class="btn pri">Speichern</button></p></div></form>
<form method="post" id="purge"><input type="hidden" name="section" value="purge"><div class="card"><h2>Alte Logs löschen</h2>
<p class="mut" style="margin-top:-4px">Einmalig: Alle Läufe, die vor dem gewählten Datum gestartet sind, werden mit ihrem Log gelöscht. Laufende Aufgaben bleiben unberührt. Die Aufbewahrung oben ändert sich dadurch nicht.</p>
<div class="row"><div style="flex:0 0 260px"><label>Läufe löschen, die gestartet sind vor dem</label><input type="date" name="purge_before" value="{{ purge.before if purge else '' }}" required></div></div>
<p style="margin-top:12px"><button class="btn" name="purge_action" value="preview">Anzahl anzeigen</button>{% if purge and purge.runs %} <button class="btn del" name="purge_action" value="delete" onclick="return confirm('Die angezeigten Läufe und ihre Logs endgültig löschen? Das lässt sich nicht rückgängig machen.')">Jetzt endgültig löschen</button>{% endif %}</p></div></form>

<form method="post"><input type="hidden" name="section" value="security"><div class="card"><h2>Anmeldung und Sicherheit</h2>
<div class="row"><div><label>Konto sperren nach so vielen Fehlversuchen</label><input type="text" inputmode="numeric" name="lock_attempts" value="{{ s.lock_attempts }}"><div class="hint">0 = nie sperren. Falsches Passwort und falscher 2FA-Code zählen.</div></div>
<div><label>Sperrdauer in Minuten</label><input type="text" inputmode="numeric" name="lock_minutes" value="{{ s.lock_minutes }}"><div class="hint">0 = dauerhaft deaktivieren, bis ein Admin es wieder freigibt. Der letzte Admin wird höchstens 15 Minuten gesperrt.</div></div></div>
{% set r2 = s.require_2fa_mode if s.require_2fa_mode in ("off", "new", "all") else "off" %}
<label>Zwei-Faktor-Anmeldung (2FA) erzwingen</label>
<div class="seg"><label><input type="radio" name="require_2fa_mode" value="off" {{ "checked" if r2 == "off" }}><span>Aus (nur pro Benutzer)</span></label>
<label><input type="radio" name="require_2fa_mode" value="new" {{ "checked" if r2 == "new" }}><span>Für neue Benutzer</span></label>
<label><input type="radio" name="require_2fa_mode" value="all" {{ "checked" if r2 == "all" }}><span>Für alle Benutzer</span></label></div>
<div class="hint">Wer 2FA einrichten muss, kann nach der Anmeldung nichts anderes tun, bis eine Authenticator-App eingerichtet ist, und kann 2FA danach nicht selbst ausschalten. „Für neue Benutzer“ setzt beim Anlegen das Häkchen „2FA erzwingen“, bestehende Benutzer bleiben, wie sie sind. „Für alle Benutzer“ gilt sofort für jedes Konto, auch für deins. Pro Benutzer schaltest du es unter Benutzer → Bearbeiten ein.</div>
{% set fm = s.fail_notify or ("lock" if s.lock_notify else "off") %}
<div class="row"><div style="flex:2"><label>Benachrichtigung über fehlgeschlagene Anmeldungen</label><select name="fail_notify">
<option value="every" {{ "selected" if fm == "every" }}>bei jedem Fehlversuch (gedrosselt) und bei Sperre</option>
<option value="lock" {{ "selected" if fm == "lock" }}>nur wenn ein Konto gesperrt wird</option>
<option value="off" {{ "selected" if fm == "off" }}>nie</option></select></div>
<div><label>Höchstens eine Meldung alle … Minuten</label><input type="text" inputmode="numeric" name="fail_notify_minutes" value="{{ s.fail_notify_minutes or 15 }}"></div></div>
<div class="hint">Versand über die Standard-Kanäle unter <a href="/settings">Benachrichtigungen</a> (Webhook, E-Mail, Telegram). Fehlversuche innerhalb der Drosselzeit werden gesammelt und mit der nächsten Meldung geschickt. Eine Sperre wird immer sofort gemeldet.</div>
<h3>IP-Adresse und Land</h3>
<label class="check"><input type="checkbox" name="trust_proxy" {{ "checked" if s.trust_proxy }}> MirrorSync läuft hinter einem Reverse-Proxy (z. B. Nginx Proxy Manager, Traefik, Caddy): IP-Adresse aus dem Header X-Forwarded-For verwenden</label>
<div class="hint">Nur einschalten, wenn wirklich ein Proxy davor sitzt, sonst kann jeder eine falsche Adresse vorgeben. Deine Adresse gerade: <code>{{ my_ip }}</code> {{ my_loc.flag }} {{ my_loc.name }}{% if fwd and not s.trust_proxy %} · Der Browser kam über einen Proxy (<code>X-Forwarded-For: {{ fwd }}</code>), Häkchen setzen.{% endif %}</div>
<h3>Passkeys</h3>
<label>Öffentliche Adresse von MirrorSync</label><input type="text" name="public_url" value="{{ s.public_url or '' }}" placeholder="https://sync.example.de">
<div class="hint">Passkeys sind an einen Domainnamen gebunden und brauchen HTTPS. Leer = die Adresse, über die du MirrorSync gerade aufrufst{% if pk_now %} (jetzt: <code>{{ pk_now }}</code>){% endif %}. Über eine IP-Adresse oder <code>http://</code> gibt es keine Passkeys. Die Adresse später zu ändern macht bestehende Passkeys unbrauchbar.</div>
<label class="check" style="margin-top:16px"><input type="checkbox" name="geoip_auto" {{ "checked" if s.geoip_auto }}> Länder-Datenbank (DB-IP Lite, ca. 8 MB) automatisch laden und erneuern</label>
{% set gsched = s.geoip_mode == "schedule" %}{% set gdow = (s.geoip_dow or "mon").split(",") %}
<label>Erneuern</label>
<div class="seg" id="gmode"><label><input type="radio" name="geoip_mode" value="interval" {{ "checked" if not gsched }} onchange="gShow()"><span>Nach Intervall</span></label><label><input type="radio" name="geoip_mode" value="schedule" {{ "checked" if gsched }} onchange="gShow()"><span>Nach Zeitplan (Uhrzeit und Wochentage)</span></label></div>
<div class="row" id="g_iv" style="{{ 'display:none' if gsched }}"><div style="flex:0 0 260px"><label>Abstand</label><select name="geoip_days">{% for d, t in [("1","täglich"),("7","jede Woche"),("14","alle 2 Wochen"),("30","monatlich"),("60","alle 2 Monate"),("90","alle 3 Monate")] %}<option value="{{ d }}" {{ "selected" if (s.geoip_days or "30") == d }}>{{ t }}</option>{% endfor %}</select></div>
<div><div class="hint" style="margin-top:28px">Geprüft wird täglich, geladen wird, sobald die Datei älter ist.</div></div></div>
<div class="row" id="g_sc" style="align-items:flex-end;{{ '' if gsched else 'display:none' }}"><div style="flex:0 0 auto"><label>Uhrzeit</label><input type="time" name="geoip_time" value="{{ s.geoip_time or '03:00' }}" style="width:130px"></div>
<div><label>Wochentage</label><div class="days">{% for v, n in [("mon","Mo"),("tue","Di"),("wed","Mi"),("thu","Do"),("fri","Fr"),("sat","Sa"),("sun","So")] %}<label><input type="checkbox" name="geoip_dow" value="{{ v }}" {{ "checked" if v in gdow }}><span>{{ n }}</span></label>{% endfor %}</div></div></div>
<div class="hint">DB-IP veröffentlicht die Lite-Datenbank einmal im Monat, häufigeres Erneuern lädt meist dieselbe Datei. Beim Zeitplan wird zur gewählten Zeit immer neu geladen.</div>
{% if gsched and next_geoip %}<div class="hint">{{ _("Nächstes Mal") }}: {{ next_geoip }} ({{ tz }})</div>{% endif %}
<script>function gShow(){const s=document.querySelector('[name=geoip_mode]:checked').value==='schedule';document.getElementById('g_iv').style.display=s?'none':'';document.getElementById('g_sc').style.display=s?'':'none'}</script>
<div class="hint">{% if geo.ok %}Datenbank: <code>{{ geo.file }}</code>{% if geo.date %} vom {{ geo.date }}{% endif %}.{% else %}<span class="fehler">Noch keine Länder-Datenbank vorhanden.</span> Ohne sie werden nur IP-Adressen angezeigt.{% endif %}
Die Abfrage erfolgt lokal im Container, es werden keine Adressen an fremde Dienste geschickt. Eigene Datei (z. B. <code>GeoLite2-Country.mmdb</code>) kannst du nach <code>config/geoip/</code> legen. {{ attribution }}</div>
<p style="margin-top:16px"><button class="btn pri">Speichern</button> <button class="btn" name="geoip_now" value="1">Speichern und Länder-Datenbank jetzt laden</button></p></div></form>

<form method="post"><input type="hidden" name="section" value="bw"><div class="card"><h2>Bandbreite (Standard)</h2>{% set bw_unit_select = true %}
<p class="mut" style="margin-top:-4px">Gilt für alle Aufgaben mit „Standard verwenden“. Jede Aufgabe kann eigene Grenzen haben.<br>Aktuell: <b>{{ bw_desc }}</b></p>
{% include "bw_editor.html" %}
{% if bw_tt %}<details style="margin-top:10px"><summary class="hint" style="cursor:pointer">rclone-Zeittabelle anzeigen</summary><pre style="margin-top:6px">--bwlimit "{{ bw_tt }}"</pre></details>{% endif %}
<p style="margin-top:16px"><button class="btn pri">Bandbreite speichern</button></p></div></form>
{% endblock %}""",
"bw_editor.html": r"""<input type="hidden" name="bw_json" id="bw_json">
{% if bw_unit_select %}<div class="row"><div style="flex:0 0 220px"><label>Einheit</label><select name="bw_unit" id="bw_unit"><option value="MB/s" {{ "selected" if bw_unit() == "MB/s" }}>MB/s (Megabyte pro Sekunde)</option><option value="Mbit/s" {{ "selected" if bw_unit() == "Mbit/s" }}>Mbit/s (Megabit pro Sekunde)</option></select></div></div>{% endif %}
<label>Außerhalb der Zeitfenster</label>
<div class="row"><div><input type="text" class="mb" inputmode="decimal" id="bw_up" placeholder="unbegrenzt"><div class="hint">Upload (zum Ziel) in <span class="bwu">MB/s</span></div></div>
<div><input type="text" class="mb" inputmode="decimal" id="bw_down" placeholder="unbegrenzt"><div class="hint">Download (von der Quelle) in <span class="bwu">MB/s</span></div></div></div>
<label style="margin-top:14px">Zeitfenster</label>
<div id="bw_rows"></div>
<p style="margin:6px 0 0"><button type="button" class="btn sm" onclick="bwAdd({days:[0,1,2,3,4],start:'08:00',end:'18:00',up:'10',down:'10'})">Vorlage: werktags 8–18 Uhr 10 MB/s (80 Mbit/s)</button>
<button type="button" class="btn sm" onclick="bwAdd()">{{ ICON.plus }} Zeitfenster</button>
<button type="button" class="btn sm" onclick="bwAdd({days:[0,1,2,3,4,5,6],start:'07:00',end:'23:00',up:'5',down:'5'})">Vorlage: tagsüber 5 MB/s (40 Mbit/s)</button></p>
<div class="bwprev" id="bw_prev"></div>
<div class="hint">Leer = unbegrenzt. 1 MB/s entspricht 8 Mbit/s. Fenster mit Ende vor dem Beginn (z. B. 22:00–06:00) gehen über Mitternacht.
Überschneiden sich Fenster, gilt das weiter unten stehende. Die Grenzen wechseln auch während eines laufenden Spiegelns.
Läuft der Container als Vermittler (A → B), bremst schon ein Wert den ganzen Durchsatz, denn alles, was von A geladen wird, geht direkt zu B.</div>
<script>
(function(){
const DD=['Mo','Di','Mi','Do','Fr','Sa','So'];let C={{ (bw_cfg or {})|tojson }};
let U='{{ bw_unit() }}';const FAC={'MB/s':1,'Mbit/s':8};
const num=v=>parseFloat(String(v).replace(',','.'));
const show=v=>{if(v===''||v==null)return '';const n=num(v);return isNaN(n)?String(v):String(+(n*FAC[U]).toFixed(3))};
const store=v=>{v=String(v).trim();if(!v)return '';const n=num(v);return isNaN(n)?v:String(+(n/FAC[U]).toFixed(4))};
const rows=document.getElementById('bw_rows');
document.getElementById('bw_up').value=show(C.up);document.getElementById('bw_down').value=show(C.down);
function el(h){const t=document.createElement('template');t.innerHTML=h.trim();return t.content.firstChild}
function units(){document.querySelectorAll('.bwu').forEach(e=>e.textContent=U)}
window.bwAdd=function(r,raw){r=r||{days:[0,1,2,3,4],start:'08:00',end:'18:00',up:'',down:''};
  const d=el('<div class="bwrow"><div><label>Tage</label><div class="days">'+DD.map((n,i)=>'<label><input type="checkbox" value="'+i+'"'+(r.days.includes(i)?' checked':'')+'><span>'+n+'</span></label>').join('')+'</div></div>'+
   '<div><label>von</label><input type="time" class="st" value="'+r.start+'"></div><div><label>bis</label><input type="time" class="en" value="'+(r.end==='24:00'?'23:59':r.end)+'"></div>'+
   '<div><label>Upload <span class="bwu"></span></label><input type="text" class="mb up" inputmode="decimal" placeholder="unbegrenzt"></div><div><label>Download <span class="bwu"></span></label><input type="text" class="mb dn" inputmode="decimal" placeholder="unbegrenzt"></div>'+
   '<div><button type="button" class="btn sm del" title="entfernen">✕</button></div></div>');
  d.querySelector('.up').value=raw?(r.up||''):show(r.up);d.querySelector('.dn').value=raw?(r.down||''):show(r.down);
  d.querySelector('.del').onclick=()=>{d.remove();bwPrev()};d.addEventListener('input',bwPrev);d.addEventListener('change',bwPrev);rows.append(d);units();bwPrev()};
function collect(){return {up:store(document.getElementById('bw_up').value),down:store(document.getElementById('bw_down').value),
  rules:[...rows.querySelectorAll('.bwrow')].map(d=>({days:[...d.querySelectorAll('.days input:checked')].map(i=>+i.value),
   start:d.querySelector('.st').value,end:d.querySelector('.en').value,up:store(d.querySelector('.up').value),down:store(d.querySelector('.dn').value)}))}}
function rate(u,d){u=u?show(u)+' '+U:'unbegrenzt';d=d?show(d)+' '+U:'unbegrenzt';return u===d?u:'↑ '+u+' / ↓ '+d}
function days(a){const s=a.join();return s==='0,1,2,3,4,5,6'?'täglich':s==='0,1,2,3,4'?'Mo–Fr':s==='5,6'?'Sa–So':a.map(i=>DD[i]).join(', ')}
window.bwPrev=function(){const c=collect();const p=c.rules.map(r=>days(r.days)+' '+r.start+'–'+r.end+': '+rate(r.up,r.down));
  p.push((c.rules.length?'sonst':'immer')+': '+rate(c.up,c.down));document.getElementById('bw_prev').textContent='Ergebnis: '+p.join(' · ')};
['bw_up','bw_down'].forEach(i=>document.getElementById(i).addEventListener('input',bwPrev));
(C.rules||[]).forEach(r=>bwAdd(r));units();bwPrev();
const us=document.getElementById('bw_unit');
if(us)us.addEventListener('change',()=>{const c=collect();U=us.value;   // Werte umrechnen, nicht verlieren
  document.getElementById('bw_up').value=show(c.up);document.getElementById('bw_down').value=show(c.down);
  [...rows.querySelectorAll('.bwrow')].forEach((d,i)=>{d.querySelector('.up').value=show(c.rules[i].up);d.querySelector('.dn').value=show(c.rules[i].down)});units();bwPrev()});
const f=document.getElementById('bw_json').form;f.addEventListener('submit',()=>{document.getElementById('bw_json').value=JSON.stringify(collect())});
})();
</script>""",
"login_log.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}{% block body %}{% include "tabs.html" %}
{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap"><h2 style="margin:0">Anmeldeverlauf{% if who %} von {{ who }}{% endif %}</h2><a class="btn" href="/users">Zurück</a></div>
<div class="chips" style="margin-top:12px">{% for k, label in [("all","Alle"),("new","Unbestätigt"),("fail","Fehlgeschlagen"),("ok","Erfolgreich")] %}<a class="chip {{ 'active' if flt == k }}" href="?f={{ k }}{% if who %}&u={{ who|urlencode }}{% endif %}">{{ label }}{% if k == "new" and unacked %} <b>{{ unacked }}</b>{% endif %}</a>{% endfor %}{% if who %}<a class="chip" href="?f={{ flt }}">alle Benutzer</a>{% endif %}</div>
{% set manage = can("users.manage") %}
<form method="post" action="/users/log/action" id="lf"><input type="hidden" name="back" value="{{ request.full_path }}">
{% if manage %}<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">
<button class="btn sm" name="action" value="ack" onclick="this.form.all.value='0'">✓ Ausgewählte bestätigen</button>
<button class="btn sm del" name="action" value="delete" onclick="this.form.all.value='0';return confirm('Ausgewählte Einträge löschen?')">Ausgewählte löschen</button>
<span style="flex:1"></span>
{% if unacked %}<button class="btn sm" name="action" value="ack" onclick="this.form.all.value='1'">✓ Alle Fehlversuche bestätigen</button>{% endif %}
<button class="btn sm del" name="action" value="delete" onclick="this.form.all.value='1';this.form.only_failed.value='1';if(confirm('Alle fehlgeschlagenen Anmeldungen löschen? Erfolgreiche bleiben erhalten.'))return true;this.form.all.value='0';return false">Alle Fehlversuche löschen</button>
<input type="hidden" name="all" value="0"><input type="hidden" name="only_failed" value="{{ '0' if flt == 'ok' else '1' }}"></div>{% endif %}
{% if entries %}<table><tr>{% if manage %}<th style="width:28px"><input type="checkbox" onclick="document.querySelectorAll('#lf input[name=id]').forEach(c=>c.checked=this.checked)" title="alle auswählen"></th>{% endif %}<th>Zeit</th><th>Benutzer</th><th>IP-Adresse</th><th class="hide-sm">Land</th><th>Ergebnis</th><th class="hide-sm">Browser</th></tr>
{% for e in entries %}{% set new = not e.ok and not e.ack %}<tr class="{{ 'new' if new }}">{% if manage %}<td>{% if not e.ok or flt == "ok" %}<input type="checkbox" name="id" value="{{ e.id }}">{% endif %}</td>{% endif %}
<td><small>{{ e.time }}</small></td><td><a href="?f={{ flt }}&u={{ e.user|urlencode }}">{{ e.user or "–" }}</a></td><td><code>{{ e.ip }}</code>
{% if e.ip in blocked_nets %}<br><span class="tag fehler">gesperrt</span>{% elif can("system.access") and not e.ok and e.iso != "LAN" %}<br><button type="button" class="btn sm del" style="margin-top:4px;padding:2px 8px" onclick="blockIp('{{ e.ip }}')">IP sperren</button>{% endif %}</td>
<td class="hide-sm">{{ e.flag }} {{ e.country or "–" }}</td>
<td>{% if e.ok %}<span class="tag ok">ok</span>{% else %}<span class="tag fehler">fehlgeschlagen</span>{% if new %} <span class="tag laeuft">neu</span>{% endif %}{% endif %}<br><small class="mut">{{ e.reason }}{% if e.ack and e.ack_by %} · bestätigt von {{ e.ack_by }}{% endif %}</small></td>
<td class="hide-sm"><small class="mut" title="{{ e.ua }}">{{ e.ua|ua }}</small></td></tr>{% endfor %}</table>
{% else %}<div class="empty">Keine Einträge.</div>{% endif %}
</form>
{% if can("system.access") %}<form method="post" action="/settings/access/block" id="bf" style="display:none"><input type="hidden" name="net"><input type="hidden" name="note"><input type="hidden" name="minutes" value="0"><input type="hidden" name="back" value="{{ request.full_path }}"></form>
<script>function blockIp(ip){const d=prompt('IP '+ip+' sperren.\nWie lange? Minuten eingeben, 0 = dauerhaft','0');if(d===null)return;const f=document.getElementById('bf');
f.net.value=ip;f.minutes.value=parseInt(d)||0;f.note.value='aus dem Anmeldeverlauf';f.submit()}</script>{% endif %}
<p class="hint">Unbestätigte Fehlversuche erscheinen als rote Zahl bei „Einstellungen“ und „Benutzer“, bis du sie bestätigst oder löschst. Gespeichert werden die letzten 1000 Anmeldeversuche in der Datenbank.{% if geo.ok %} {{ attribution }}{% else %} Für die Länder unter Einstellungen → Allgemein die Länder-Datenbank laden.{% endif %}</p>
</div>
{% endblock %}""",
"audit.html": r"""{% extends "base.html" %}{% block title %}Audit-Log{% endblock %}
{% block subtitle %}<p>Wer hat wann was gemacht: Änderungen an Aufgaben, Zeitplänen, Speicherorten, Benutzern, Rollen, Einstellungen und Zugriffsregeln, Starts und Stopps, An- und Abmeldungen.</p>{% endblock %}
{% block actions %}<a class="btn" href="/audit/export.csv{% if args %}?{{ args|urlencode }}{% endif %}">⬇ CSV exportieren</a>{% endblock %}
{% block body %}
<div class="card">
<form method="get" class="row afilter" style="align-items:flex-end">
<div style="flex:2"><label>Suche</label><input type="text" name="q" value="{{ f.q }}" placeholder="z. B. Aufgabenname, IP, Feld, Wert"></div>
<div><label>Bereich</label><select name="cat"><option value="">alle</option>{% for k, v in cats.items() %}<option value="{{ k }}" {{ "selected" if f.cat == k }}>{{ v }}</option>{% endfor %}</select></div>
<div><label>Benutzer</label><select name="user"><option value="">alle</option>{% for u in users %}<option {{ "selected" if f.user|lower == u|lower }}>{{ u }}</option>{% endfor %}</select></div>
<div><label>von</label><input type="date" name="from" value="{{ f.day_from }}"></div>
<div><label>bis</label><input type="date" name="to" value="{{ f.day_to }}"></div>
<div style="flex:0 0 auto;display:flex;gap:6px"><button class="btn pri">Filtern</button>{% if args %}<a class="btn" href="/audit">Zurücksetzen</a>{% endif %}</div>
</form></div>
<div class="card" style="padding:6px 8px">
{% if entries %}<table class="audit"><tr><th>Zeit</th><th>Benutzer</th><th>Bereich</th><th>Aktion</th><th>Details</th></tr>
{% for e in entries %}<tr class="arow" data-i="{{ loop.index }}" title="Klicken für alle Details">
<td style="white-space:nowrap"><small>{{ e.ts[8:10] }}.{{ e.ts[5:7] }}.{{ e.ts[:4] }}<br>{{ e.ts[11:] }}</small></td>
<td><a href="?user={{ e.user|urlencode }}">{{ e.user }}</a>{% if e.ip %}<br><small class="mut">{{ e.flag }} <code>{{ e.ip }}</code></small>{% endif %}</td>
<td><a class="tag" href="?cat={{ e.cat }}" style="text-decoration:none">{{ cats.get(e.cat, e.cat) }}</a></td>
<td><b>{{ e.action }}</b>{% if e.target %}<br><span>{{ e.target }}</span>{% endif %}</td>
<td>{% if e.detail %}<div class="mut">{{ e.detail }}</div>{% endif %}
{% if e.changes %}<table class="chg">{% for c in e.changes %}<tr><td class="mut">{{ c.label }}</td>{% if c.secret %}<td colspan="2"><i>geändert</i></td>{% elif e.action == "angelegt" %}<td colspan="2"><code>{{ c.new }}</code></td>{% else %}<td><del>{{ c.old }}</del></td><td><ins>{{ c.new }}</ins></td>{% endif %}</tr>{% endfor %}</table>{% endif %}</td>
</tr>{% endfor %}</table>
<div hidden>{% for e in entries %}<div id="ad-{{ loop.index }}">
<h2 style="margin:0 0 4px">{{ e.action }}{% if e.target %} · {{ e.target }}{% endif %}</h2>
<table class="adt">
<tr><th>Zeit</th><td>{{ e.ts[8:10] }}.{{ e.ts[5:7] }}.{{ e.ts[:4] }} {{ e.ts[11:] }}</td></tr>
<tr><th>Ausgeführt von</th><td>{{ e.user }}</td></tr>
{% if e.ip %}<tr><th>IP-Adresse</th><td><code>{{ e.ip }}</code> {{ e.flag }} {{ e.country }}</td></tr>{% endif %}
<tr><th>Bereich</th><td>{{ cats.get(e.cat, e.cat) }}</td></tr>
{% if e.target %}<tr><th>Objekt</th><td>{{ e.target }}</td></tr>{% endif %}
{% if e.detail %}<tr><th>Details</th><td>{{ e.detail }}</td></tr>{% endif %}
{% for k, v in (e.info or {}).items() %}<tr><th>{{ k }}</th><td>{% if "\n" in v %}<pre class="apre">{{ v }}</pre>{% else %}{{ v }}{% endif %}</td></tr>{% endfor %}
</table>
{% if e.changes %}<h3 style="margin:16px 0 6px">{{ "Inhalt" if e.action in ("angelegt", "gelöscht") else "Änderungen" }} ({{ e.changes|length }})</h3>
{% for c in e.changes %}<div class="achg"><b>{{ c.label }}</b>{% if c.label != c.f %} <small class="mut"><code>{{ c.f }}</code></small>{% endif %}
{% if c.secret %}<div class="mut"><i>geändert</i> (Geheimnisse werden nie gespeichert)</div>
{% elif c.added is defined and (c.added or c.removed) %}
{% for x in c.added %}<div class="aadd">+ {{ x }}</div>{% endfor %}{% for x in c.removed %}<div class="adel">− {{ x }}</div>{% endfor %}
{% elif c.old_full is defined %}<div class="arow2">{% if e.action != "angelegt" %}<div><small class="mut">vorher</small><pre class="apre">{{ c.old_full or "–" }}</pre></div>{% endif %}{% if e.action != "gelöscht" %}<div><small class="mut">nachher</small><pre class="apre">{{ c.new_full or "–" }}</pre></div>{% endif %}</div>
{% elif e.action == "angelegt" %}<div><code>{{ c.new }}</code></div>
{% elif e.action == "gelöscht" %}<div><code>{{ c.old }}</code></div>
{% else %}<div><del>{{ c.old }}</del> → <ins>{{ c.new }}</ins></div>{% endif %}</div>{% endfor %}{% endif %}
<p class="mut" style="margin-top:12px"><small>Eintrag {{ e.id }}</small></p>
</div>{% endfor %}</div>
<dialog id="audlg" class="adlg"><div id="audbody"></div><p style="text-align:right;margin:12px 0 0"><button type="button" class="btn" onclick="document.getElementById('audlg').close()">Schließen</button></p></dialog>
<style>.arow{cursor:pointer}.arow:hover td{background:var(--hover,rgba(99,102,241,.06))}.adlg{max-width:min(860px,94vw);width:100%;border:1px solid var(--bd);border-radius:12px;background:var(--card);color:var(--fg);padding:18px 20px}
.adlg::backdrop{background:rgba(0,0,0,.35)}.adt{width:100%}.adt th{text-align:left;width:190px;vertical-align:top;color:var(--mut);font-weight:500;padding:4px 8px 4px 0}.adt td{padding:4px 0;word-break:break-word}
.apre{white-space:pre-wrap;word-break:break-word;max-height:320px;overflow:auto;background:var(--bg);border:1px solid var(--bd);border-radius:8px;padding:8px;margin:2px 0;font-size:12px}
.achg{padding:8px 0;border-top:1px solid var(--bd)}.aadd{color:var(--ok);font-family:monospace;font-size:13px}.adel{color:var(--err);font-family:monospace;font-size:13px}.arow2{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}</style>
<script>document.querySelectorAll('.arow').forEach(r=>r.addEventListener('click',e=>{if(e.target.closest('a'))return;
  document.getElementById('audbody').innerHTML=document.getElementById('ad-'+r.dataset.i).innerHTML;document.getElementById('audlg').showModal()}));
document.getElementById('audlg').addEventListener('click',e=>{if(e.target.id==='audlg')e.target.close()});</script>
{% if pages > 1 %}<div style="display:flex;gap:6px;justify-content:center;padding:12px;align-items:center">{% if page > 1 %}<a class="btn sm" href="?{{ dict(args, page=page-1)|urlencode }}">‹ neuer</a>{% endif %}<small class="mut">Seite {{ page }} von {{ pages }}</small>{% if page < pages %}<a class="btn sm" href="?{{ dict(args, page=page+1)|urlencode }}">älter ›</a>{% endif %}</div>{% endif %}
{% else %}<div class="empty">Keine Einträge{% if args %} für diesen Filter{% endif %}.</div>{% endif %}
</div>
<p class="hint">{{ total }} Einträge{% if args %} gefunden{% endif %}. Passwörter, Tokens und andere Geheimnisse werden nie gespeichert, nur dass sie geändert wurden.
Aufbewahrung: {{ keep if keep != "0" else "unbegrenzt" }}{% if keep != "0" %} Tage{% endif %}{% if can("system.settings") %} (<a href="/settings/general">ändern</a>){% endif %}. Gespeichert in der Datenbank.</p>
{% endblock %}""",
"schedules.html": r"""{% extends "base.html" %}{% block title %}Zeitpläne{% endblock %}
{% block subtitle %}<p>Wann welche Aufgabe startet. Änderungen hier gelten sofort auch in der Aufgabe und umgekehrt.</p>{% endblock %}
{% block actions %}<span class="savestate" id="state"></span>{% endblock %}
{% block body %}
<div id="err" class="msg err" style="display:none"></div>
<div class="card" id="zeit"><h2>🕒 Nach Uhrzeit</h2><div id="sec-time"></div></div>
<div class="card" id="live"><h2>⚡ Fortlaufend (Live)</h2><p class="hint" style="margin-top:-6px">„Wie Spiegeln“ gleicht alle paar Minuten Quelle und Ziel ab, inklusive Löschen. „Schnell“ kopiert nur neue und geänderte Dateien, ohne zu löschen, und spiegelt optional zu einer Uhrzeit oder nach Intervall komplett, damit auch Löschungen ankommen. Läufe ohne Änderung erscheinen nicht im Verlauf.</p><div id="sec-live"></div></div>
<div class="card" id="kette"><h2>⛓ Nach einer anderen Aufgabe</h2>
<p class="hint" style="margin-top:-6px">Jede Kette beginnt mit einer Aufgabe nach Uhrzeit, einer Live-Aufgabe (nach ihrem vollen Abgleich) oder einer manuellen Aufgabe. Darunter laufen die Aufgaben von oben nach unten nacheinander.
Reihenfolge per Drag &amp; Drop (am ⠿ greifen) oder mit ↑ ↓ ändern. Aufgaben lassen sich auch zwischen Ketten und aus „Nur manuell“ hierher ziehen.</p>
<div id="sec-after"></div>
<div id="newchain" style="margin-top:6px"></div></div>
<div class="card" id="manuell"><h2>✋ Nur manuell</h2><p class="hint" style="margin-top:-6px">Starten nur über „Start“ in der Übersicht. Hierher ziehen nimmt eine Aufgabe aus ihrer Kette.</p><div id="manual-drop" class="drop"></div></div>
<script>
let D={{ data|tojson }};const E=D.edit;const DD=['Mo','Di','Mi','Do','Fr','Sa','So'];
const esc=t=>String(t??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const $=id=>document.getElementById(id);
function state(t,bad){const s=$('state');s.textContent=t;s.style.color=bad?'var(--err)':'';if(!bad&&t)setTimeout(()=>{if(s.textContent===t)s.textContent=''},2500)}
function showErr(t){const e=$('err');e.style.display=t?'block':'none';e.textContent=t||''}
async function api(url,body){state('Speichere…');showErr('');
  try{const r=await fetch(url,{method:body?'POST':'GET',headers:{'Content-Type':'application/json',Accept:'application/json'},body:body?JSON.stringify(body):undefined});
    const j=await r.json();if(!r.ok||j.ok===false){showErr(j.error||'Fehler beim Speichern.');state('',true);await reload();return false}
    state('✓ Gespeichert');return j}catch(e){showErr('Keine Verbindung zum Server.');state('',true);return false}}
async function reload(){const r=await fetch('/schedules/data',{headers:{Accept:'application/json'}});D=await r.json();render()}
function parseCron(v){const m=(v||'').trim().match(/^(\d{1,2}) (\d{1,2}) \* \* (\*|[0-6](?:[-,][0-6])*)$/);if(!m)return null;
  const days=m[3]==='*'?[0,1,2,3,4,5,6]:m[3].split(',').flatMap(p=>{const [a,b]=p.split('-').map(Number);return b===undefined?[a]:Array.from({length:b-a+1},(_,i)=>a+i)});
  return {t:String(m[2]).padStart(2,'0')+':'+String(m[1]).padStart(2,'0'),days}}
function toCron(t,days){const [h,m]=(t||'03:00').split(':');const d=[...days].sort();let dw='*';
  if(d.length&&d.length<7){const g=[];d.forEach(x=>{const l=g[g.length-1];if(l&&x===l[1]+1)l[1]=x;else g.push([x,x])});dw=g.map(([a,b])=>a===b?a:(b===a+1?a+','+b:a+'-'+b)).join(',')}
  return (+m)+' '+(+h)+' * * '+dw}
function descendants(id){const out=new Set([id]);let grow=true;while(grow){grow=false;for(const j of Object.values(D.jobs))if(j.trigger==='after'&&out.has(j.after_job)&&!out.has(j.id)){out.add(j.id);grow=true}}return out}
function trigSelect(j){if(!E)return '';return '<select class="trig" title="Startart"><option value="time"'+(j.trigger==='time'?' selected':'')+'>🕒 Nach Uhrzeit</option><option value="live"'+(j.trigger==='live'?' selected':'')+'>⚡ Fortlaufend (Live)</option><option value="after"'+(j.trigger==='after'?' selected':'')+'>⛓ Nach Aufgabe</option><option value="manual"'+(j.trigger==='manual'?' selected':'')+'>✋ Nur manuell</option></select>'}
function nameCell(j,extra){return '<div class="nm"><b><a href="/job/'+j.id+'" style="color:inherit;text-decoration:none">'+esc(j.name)+'</a>'+(j.running?' <span class="tag laeuft">läuft</span>':'')+(j.paused?' <span class="tag pausetag" title="'+(j.pause_chain==='stop'?'In der Kette: hält die Kette an':'In der Kette: wird übersprungen')+'">'+esc(j.pause_text)+'</span>':'')+'</b><div class="path">'+esc(j.path)+'</div>'+(extra||'')+'</div>'}
function bindTrig(el,j){const s=el.querySelector('.trig');if(!s)return;s.onchange=()=>{
  if(s.value==='after'){askParent(el,j,s);return}
  api('/schedules/job/'+j.id,{trigger:s.value,schedule:j.schedule,enabled:true}).then(ok=>ok&&reload())}}
function askParent(el,j,s){const bad=descendants(j.id);const opts=D.order.filter(id=>!bad.has(id)).map(id=>'<option value="'+id+'">'+esc(D.jobs[id].name)+'</option>').join('');
  if(!opts){showErr('Es gibt keine andere Aufgabe, nach der diese starten könnte.');s.value=j.trigger;return}
  const box=document.createElement('div');box.className='ctl';box.style.flexBasis='100%';
  box.innerHTML='<span>Starten nach</span><select class="par">'+opts+'</select><select class="wh"><option value="ok">nur bei Erfolg</option><option value="always">immer</option></select><button type="button" class="btn sm pri">Übernehmen</button><button type="button" class="btn sm">Abbrechen</button>';
  el.append(box);const [ok,cancel]=box.querySelectorAll('button');
  cancel.onclick=()=>{box.remove();s.value=j.trigger};
  ok.onclick=()=>api('/schedules/job/'+j.id,{trigger:'after',after_job:box.querySelector('.par').value,when:box.querySelector('.wh').value,enabled:true}).then(r=>r&&reload())}
function timeRow(j){const el=document.createElement('div');el.className='sch';const pc=parseCron(j.schedule);
  const days=pc?pc.days:[1,2,3,4,5,6,0];
  el.innerHTML=nameCell(j,'<small class="mut">'+(j.enabled&&j.next_run?'nächster Lauf '+esc(j.next_run):'<span class="fehler">Zeitplan aus</span>')+'</small>')+
   '<div class="ctl">'+trigSelect(j)+
   (pc?'<input type="time" class="tm" value="'+pc.t+'"><span class="days">'+[1,2,3,4,5,6,0].map(d=>'<label><input type="checkbox" value="'+d+'"'+(days.includes(d)?' checked':'')+'><span>'+DD[(d+6)%7]+'</span></label>').join('')+'</span>'
       :'<input type="text" class="cr" value="'+esc(j.schedule)+'" style="width:150px" title="Cron-Ausdruck">')+
   '<label class="check" style="margin:0"><input type="checkbox" class="en"'+(j.enabled?' checked':'')+'> '+'aktiv'+'</label>'+
   (E?'<button type="button" class="btn sm pri sv">Speichern</button>':'')+'</div>';
  if(!E)el.querySelectorAll('input').forEach(i=>i.disabled=true);
  bindTrig(el,j);const sv=el.querySelector('.sv');
  if(sv)sv.onclick=()=>{const cr=el.querySelector('.cr');const sched=cr?cr.value.trim():toCron(el.querySelector('.tm').value,[...el.querySelectorAll('.days input:checked')].map(i=>+i.value));
    api('/schedules/job/'+j.id,{trigger:'time',schedule:sched,enabled:el.querySelector('.en').checked}).then(ok=>ok&&reload())};
  return el}
function liveRow(j){const el=document.createElement('div');el.className='sch';const ev=(j.full||'').match(/^@every\s+(\d+)\s*([mh])$/);
  const pc=ev?null:(j.full?parseCron(j.full):parseCron('0 3 * * *'));const days=pc?pc.days:[1,2,3,4,5,6,0];
  const kind=ev?'every':(pc||!j.full?'time':'cron');const fast=j.live_mode==='fast',tw=j.direction==='bisync';
  el.innerHTML=nameCell(j,'<small class="mut">'+(j.enabled?esc(j.live_text)+' · '+esc(j.full_text)+(fast&&j.next_run?' (nächster '+esc(j.next_run)+')':'')+(j.live_checked?' · zuletzt geprüft '+esc(j.live_checked.slice(11,16)):''):'<span class="fehler">Live aus</span>')+'</small>')+
   '<div class="ctl">'+trigSelect(j)+
   '<select class="lm" title="'+'Bei jeder Runde'+'"'+(tw?' style="display:none"':'')+'><option value="mirror"'+(fast?'':' selected')+'>'+'🪞 Wie Spiegeln (inkl. Löschen)'+'</option><option value="fast"'+(fast?' selected':'')+'>'+'⚡ Schnell (ohne Löschen)'+'</option></select>'+
   '<span>alle</span><input type="number" class="iv" min="1" max="1440" value="'+j.interval+'" style="width:70px"><span>Min.</span>'+
   '<span class="fullc" style="display:contents"><label class="check" style="margin:0"><input type="checkbox" class="fon"'+(j.full?' checked':'')+'> '+'voll'+'</label>'+
   '<select class="fk"><option value="time"'+(kind==='time'?' selected':'')+'>'+'Uhrzeit'+'</option><option value="every"'+(kind==='every'?' selected':'')+'>'+'Intervall'+'</option><option value="cron"'+(kind==='cron'?' selected':'')+'>Cron</option></select>'+
   '<span class="fk-time" style="display:contents"><input type="time" class="tm" value="'+(pc?pc.t:'03:00')+'"><span class="days">'+[1,2,3,4,5,6,0].map(d=>'<label><input type="checkbox" value="'+d+'"'+(days.includes(d)?' checked':'')+'><span>'+DD[(d+6)%7]+'</span></label>').join('')+'</span></span>'+
   '<span class="fk-every" style="display:contents"><input type="number" class="fn" min="1" max="720" value="'+(ev?ev[1]:6)+'" style="width:70px"><select class="fu"><option value="h"'+(ev&&ev[2]==='m'?'':' selected')+'>'+'Std.'+'</option><option value="m"'+(ev&&ev[2]==='m'?' selected':'')+'>'+'Min.'+'</option></select></span>'+
   '<span class="fk-cron" style="display:contents"><input type="text" class="cr" value="'+esc(kind==='cron'?j.full:'0 3 * * *')+'" style="width:150px" title="'+'Cron-Ausdruck für den vollen Abgleich'+'"></span></span>'+
   '<label class="check" style="margin:0"><input type="checkbox" class="en"'+(j.enabled?' checked':'')+'> '+'aktiv'+'</label>'+
   (E?'<button type="button" class="btn sm pri sv">Speichern</button>':'')+'</div>';
  const q=s=>el.querySelector(s);
  const vis=()=>{const f=!tw&&q('.lm').value==='fast',k=q('.fk').value;q('.fullc').style.display=f?'contents':'none';
    ['time','every','cron'].forEach(x=>q('.fk-'+x).style.display=x===k?'contents':'none')};
  q('.lm').onchange=vis;q('.fk').onchange=vis;vis();
  if(!E)el.querySelectorAll('input,select.lm,select.fk,select.fu').forEach(i=>i.disabled=true);
  bindTrig(el,j);const sv=q('.sv');
  if(sv)sv.onclick=()=>{const k=q('.fk').value;let full='';
    if(q('.fon').checked)full=k==='cron'?q('.cr').value.trim():k==='every'?'@every '+(parseInt(q('.fn').value)||1)+q('.fu').value:toCron(q('.tm').value,[...el.querySelectorAll('.days input:checked')].map(i=>+i.value));
    api('/schedules/job/'+j.id,{trigger:'live',mode:q('.lm').value,interval:parseInt(q('.iv').value)||1,full:full,enabled:q('.en').checked}).then(ok=>ok&&reload())};
  return el}
function manualRow(j){const el=document.createElement('div');el.className='sch';el.dataset.id=j.id;
  el.innerHTML=(E?'<span class="handle" title="ziehen">⠿</span>':'')+nameCell(j)+'<div class="ctl">'+trigSelect(j)+'</div>';
  bindTrig(el,j);if(E)drag(el);return el}
function chainRow(j){const el=document.createElement('div');el.className='sch';el.dataset.id=j.id;
  el.innerHTML=(E?'<span class="handle" title="ziehen">⠿</span>':'')+nameCell(j)+'<div class="ctl">'+
   (E?'<select class="wh"><option value="ok"'+(j.when!=='always'?' selected':'')+'>nur bei Erfolg</option><option value="always"'+(j.when==='always'?' selected':'')+'>'+'immer'+'</option></select>'
      +'<label class="check" style="margin:0"><input type="checkbox" class="en"'+(j.enabled?' checked':'')+'> '+'aktiv'+'</label>'
      +'<button type="button" class="btn sm up" title="nach oben">↑</button><button type="button" class="btn sm dn" title="nach unten">↓</button>'+trigSelect(j)
      :'<small>'+(j.when==='always'?'immer':'nur bei Erfolg')+(j.enabled?'':' · '+'aus')+'</small>')+'</div>';
  if(E){bindTrig(el,j);drag(el);el.querySelector('.wh').onchange=saveChains;el.querySelector('.en').onchange=saveChains;
    el.querySelector('.up').onclick=()=>{const p=el.previousElementSibling;if(p&&p.classList.contains('sch')){el.parentNode.insertBefore(el,p);saveChains()}};
    el.querySelector('.dn').onclick=()=>{const n=el.nextElementSibling;if(n&&n.classList.contains('sch')){el.parentNode.insertBefore(n,el);saveChains()}}}
  return el}
let dragEl=null;
function drag(el){el.draggable=true;el.addEventListener('dragstart',e=>{dragEl=el;el.classList.add('dragging');e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',el.dataset.id)});
  el.addEventListener('dragend',()=>{el.classList.remove('dragging');document.querySelectorAll('.drop.over').forEach(d=>d.classList.remove('over'))})}
function dropZone(z,onDrop){z.addEventListener('dragover',e=>{if(!dragEl)return;e.preventDefault();z.classList.add('over');
  const after=[...z.querySelectorAll('.sch:not(.dragging)')].find(c=>e.clientY<c.getBoundingClientRect().top+c.offsetHeight/2);
  const ph=z.querySelector('.empty-drop');if(ph)ph.remove();
  if(after)z.insertBefore(dragEl,after);else z.append(dragEl)});
  z.addEventListener('dragleave',e=>{if(!z.contains(e.relatedTarget))z.classList.remove('over')});
  z.addEventListener('drop',e=>{e.preventDefault();z.classList.remove('over');const el=dragEl;dragEl=null;onDrop(el)})}
function collectChains(){return [...document.querySelectorAll('.chainbox')].map(b=>({root:b.dataset.root,
  items:[...b.querySelectorAll('.drop .sch')].map(r=>({id:r.dataset.id,when:(r.querySelector('.wh')||{}).value||'ok',enabled:r.querySelector('.en')?r.querySelector('.en').checked:true}))}))}
async function saveChains(){const ok=await api('/schedules/chains',{chains:collectChains()});await reload()}
function render(){
  const st=$('sec-time');st.innerHTML='';const times=D.order.map(id=>D.jobs[id]).filter(j=>j.trigger==='time');
  times.forEach(j=>st.append(timeRow(j)));if(!times.length)st.innerHTML='<div class="empty" style="padding:14px">Keine Aufgabe startet nach Uhrzeit.</div>';
  const sl=$('sec-live');sl.innerHTML='';const lives=D.order.map(id=>D.jobs[id]).filter(j=>j.trigger==='live');
  lives.forEach(j=>sl.append(liveRow(j)));if(!lives.length)sl.innerHTML='<div class="empty" style="padding:14px">Keine Aufgabe läuft fortlaufend. Stelle bei einer Aufgabe die Startart auf „Fortlaufend (Live)“.</div>';
  const sa=$('sec-after');sa.innerHTML='';const inChain=new Set();
  D.chains.forEach(c=>{inChain.add(c.root);c.items.forEach(i=>inChain.add(i))});
  D.chains.forEach(c=>sa.append(chainBox(c.root,c.items)));
  const orphans=D.order.map(id=>D.jobs[id]).filter(j=>j.trigger==='after'&&!inChain.has(j.id));
  if(orphans.length){const b=document.createElement('div');b.className='msg info';b.innerHTML='Ohne sichtbaren Vorgänger: '+orphans.map(j=>'<a href="/job/'+j.id+'">'+esc(j.name)+'</a>').join(', ');sa.append(b)}
  if(!D.chains.length)sa.innerHTML+='<div class="empty" style="padding:14px">Noch keine Kette. Stelle bei einer Aufgabe die Startart auf „Nach Aufgabe“ oder starte unten eine Kette.</div>';
  if(D.branched)sa.innerHTML+='<p class="hint">Hinweis: Einige Aufgaben starten parallel nach derselben Aufgabe. Hier werden sie nacheinander angezeigt; sobald du die Reihenfolge änderst, laufen sie wie angezeigt nacheinander.</p>';
  const nc=$('newchain');nc.innerHTML='';
  if(E){const roots=D.order.filter(id=>D.jobs[id].trigger!=='after'&&!D.chains.some(c=>c.root===id));
    if(roots.length){nc.innerHTML='<div class="ctl" style="display:flex;gap:8px;flex-wrap:wrap;align-items:center"><span>Neue Kette beginnen mit</span><select id="ncroot" style="width:auto">'+roots.map(id=>'<option value="'+id+'">'+esc(D.jobs[id].name)+'</option>').join('')+'</select><button type="button" class="btn sm" id="ncbtn">'+'＋ Kette'+'</button></div>';
      $('ncbtn').onclick=()=>{const r=$('ncroot').value;sa.querySelectorAll('.empty').forEach(e=>e.remove());sa.append(chainBox(r,[]));$('ncroot').querySelector('option[value="'+r+'"]').remove();if(!$('ncroot').options.length)nc.innerHTML=''}}}
  const md=$('manual-drop');md.innerHTML='';const man=D.order.map(id=>D.jobs[id]).filter(j=>j.trigger==='manual');
  man.forEach(j=>md.append(manualRow(j)));if(!man.length)md.innerHTML='<div class="empty-drop" style="margin-left:0">Keine manuellen Aufgaben.'+(E?' Aus einer Kette hierher ziehen, um sie herauszunehmen.':'')+'</div>';
}
function chainBox(root,items){const r=D.jobs[root];const b=document.createElement('div');b.className='chainbox';b.dataset.root=root;
  const how=r.trigger==='time'?('🕒 '+esc(r.text||r.schedule)+(r.enabled&&r.next_run?' · nächster Lauf '+esc(r.next_run):' · Zeitplan aus'))
    :r.trigger==='live'?('⚡ '+esc(r.live_text)+' · Folgeaufgaben nach dem vollen Abgleich'+(r.next_run?' ('+esc(r.next_run)+')':'')):'✋ '+'manuell';
  b.innerHTML='<div class="chainhead"><div class="nm"><b>'+esc(r.name)+'</b><small class="mut">'+how+'</small></div><small class="mut">Start der Kette</small></div><div class="drop"></div>';
  const z=b.querySelector('.drop');items.forEach(id=>z.append(chainRow(D.jobs[id])));
  if(!items.length)z.innerHTML='<div class="empty-drop">Aufgabe hierher ziehen</div>';
  if(E)dropZone(z,()=>saveChains());return b}
if(E)dropZone($('manual-drop'),el=>{const id=el.dataset.id;api('/schedules/job/'+id,{trigger:'manual'}).then(()=>saveChains())});
render();
</script>
{% endblock %}""",
"dashboard_tiles.html": r"""{% for t in layout %}{% set x = d.get(t.id) or {} %}<section class="dtile" data-id="{{ t.id }}" data-w="{{ t.w }}" data-h="{{ t.h }}" data-cfg="{{ t|tojson|forceescape }}" style="grid-column:span {{ t.w }};grid-row:span {{ t.h }}">
<div class="dhead"><span class="dgrip" title="Ziehen zum Verschieben">⠿</span><h3>{{ titles.get(t.id, '') }}</h3><span style="flex:1"></span><span class="dedit"><button type="button" class="btn sm" onclick="dOpen(this)" title="Bausteine bearbeiten">✎</button><button type="button" class="btn sm" onclick="dMove(this,-1)" title="Nach vorne">↑</button><button type="button" class="btn sm" onclick="dMove(this,1)" title="Nach hinten">↓</button><small class="dsz mut"></small><button type="button" class="btn sm del" onclick="dHide(this)" title="Ausblenden">✕</button></span></div>
<div class="dbody">
{% if x.error %}<p class="fehler"><span>Fehler in dieser Kachel:</span> {{ x.error }}</p>
{% elif x.view == "number" %}<div class="dnums">{% for n in x.numbers %}<a {% if n.link %}href="{{ n.link }}"{% endif %}><b class="{{ n.cls }}">{{ n.value }}</b><span>{{ n.label }}</span></a>{% endfor %}</div>
{% elif x.view == "list" %}{% if x.rows %}<table>{% if x.cols|selectattr('label')|list %}<tr>{% for c in x.cols %}<th class="{{ 'num' if c.key in ('copied','deleted','errors') }}">{{ c.label }}</th>{% endfor %}</tr>{% endif %}
{% for r in x.rows %}<tr {% if r.link %}class="click" onclick="location='{{ r.link }}'"{% endif %}>{% for c in x.cols %}{% set v = r.get(c.key) %}<td class="{{ 'num' if c.key in ('copied','deleted','errors') }}{{ ' mut' if c.key in ('started','start','last_run','at','time','ts') }}">{% if c.key == "status_text" %}<span class="tag {{ r.status }}">{{ v }}</span>{% elif c.key in ("name", "label") %}<b>{{ v }}</b>{% else %}{{ "–" if v is none or v == "" else v }}{% endif %}</td>{% endfor %}</tr>{% endfor %}</table>{% if x.total > x.rows|length %}<p class="mut" style="margin:6px 0 0"><small><span>weitere Einträge:</span> {{ x.total - x.rows|length }}</small></p>{% endif %}
{% else %}<p class="mut">Keine Einträge.</p>{% endif %}
{% elif x.view == "bar" %}{% if x.bars %}{% for b in x.bars %}<div class="dbarrow"><span class="dbl">{% if b.link %}<a href="{{ b.link }}">{{ b.label }}</a>{% else %}{{ b.label }}{% endif %}</span><span class="dbt"><i class="{{ b.cls }}" style="width:{{ [100, (100 * b.value / (b.max or 1))|round|int]|min }}%"></i></span><span class="dbv">{{ b.text }}</span></div>{% endfor %}
{% else %}<p class="mut">Keine Einträge.</p>{% endif %}
{% elif x.view == "pie" %}{% if x.pies %}<div class="dpies">{% for pc in x.pies %}<div class="dpie">{% if pc.title %}<b class="dpt">{{ pc.title }}</b>{% endif %}<div class="dpw"><div class="dpc" style="background:{{ pc.gradient }}"><span>{{ pc.center }}</span></div>
<div class="dpl">{% for sl in pc.slices %}<div><i style="background:{{ sl.color }}"></i>{{ sl.label }} <small class="mut">{{ sl.value }} · {{ sl.pct }} %</small></div>{% endfor %}</div></div></div>{% endfor %}</div>
{% else %}<p class="mut">Keine Einträge.</p>{% endif %}
{% elif x.view == "spark" %}<div class="dspk"><div><b>{{ x.value }}</b><span>{{ x.label }}</span></div><svg viewBox="0 0 300 100" preserveAspectRatio="none" aria-hidden="true"><polyline points="{{ x.points }}" fill="none" stroke="var(--acc)" stroke-width="2.5" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></svg><small class="mut">{{ x.range }}</small></div>
{% elif x.view == "line" %}{% if x.empty %}<p class="mut">Keine Einträge.</p>{% else %}<div class="dchart"><span class="dymax mut">{{ x.max_text }}</span><svg viewBox="0 0 300 100" preserveAspectRatio="none">
{% for s in x.series %}{% if s.area %}<polygon points="{{ s.area }}" fill="var(--acc-soft)"/>{% endif %}<polyline points="{{ s.points }}" fill="none" stroke="{{ s.color }}" stroke-width="2.5" vector-effect="non-scaling-stroke" stroke-linejoin="round"/>{% endfor %}
{% for c in x.cols %}<rect x="{{ (300 * loop.index0 / x.cols|length)|round(2) }}" y="0" width="{{ (300 / x.cols|length)|round(2) }}" height="100" fill="transparent"><title>{{ c.label }} · {{ c.text }}</title></rect>{% endfor %}</svg>
<div class="dxl mut"><span>{{ x.first }}</span><span>{{ x.mid }}</span><span>{{ x.last }}</span></div></div>
<div class="dleg">{% for s in x.series %}<span><i style="background:{{ s.color }}"></i>{{ s.label }} <small class="mut">{{ s.total }}</small></span>{% endfor %}</div>{% endif %}
{% elif x.view == "stacked" %}{% if x.empty %}<p class="mut">Keine Einträge.</p>{% else %}<div class="dchart"><span class="dymax mut">{{ x.max_text }}</span><div class="dstk">{% for b in x.bars %}<div class="dstc" title="{{ b.title }}"><div style="height:{{ b.h }}%">{% for g in b.segs %}<i style="height:{{ g.pct }}%;background:{{ g.color }}"></i>{% endfor %}</div></div>{% endfor %}</div>
<div class="dstx mut">{% for b in x.bars %}<span>{{ b.label if b.tick }}</span>{% endfor %}</div></div>
<div class="dleg">{% for l in x.legend %}<span><i style="background:{{ l.color }}"></i>{{ l.label }} <small class="mut">{{ l.n }}</small></span>{% endfor %}</div>{% endif %}
{% elif x.view == "gauge" %}{% if x.gauges %}<div class="dgauges">{% for gg in x.gauges %}<div class="dgauge"><svg viewBox="0 0 120 68"><path d="M10 60 A50 50 0 0 1 110 60" pathLength="100" fill="none" stroke="var(--bd)" stroke-width="11" stroke-linecap="round"/><path class="g{{ gg.cls }}" d="M10 60 A50 50 0 0 1 110 60" pathLength="100" fill="none" stroke-width="11" stroke-linecap="round" stroke-dasharray="{{ gg.pct }} 100"/><text x="60" y="56" text-anchor="middle">{{ gg.text }}</text></svg><b>{{ gg.title }}</b><small class="mut">{{ gg.sub }}</small></div>{% endfor %}</div>
{% else %}<p class="mut">Keine Einträge.</p>{% endif %}
{% elif x.view == "heatmap" %}<div class="dheat" style="grid-template-columns:repeat({{ x.weeks }},12px)">{% for c in x.cells %}{% if c.empty %}<i class="e"></i>{% else %}<i class="h{{ c.state }}" style="opacity:{{ 1 if c.level == 0 else (0.35 + 0.65 * c.level / 4)|round(2) }}" title="{{ c.date }}: {{ c.n }} {{ x.noun }}{% if c.bad %} · {{ x.bad_label }} {{ c.bad }}{% endif %}"></i>{% endif %}{% endfor %}</div>
<div class="dleg"><span class="mut"><small>{{ x.total }} {{ x.noun }}</small></span><span><i class="hnone"></i><small>0</small></span>{% for lg in x.legend %}<span><i class="h{{ lg.cls }}"></i><small>{{ lg.label }}</small></span>{% endfor %}</div>
{% elif x.view == "timeline" %}{% if x.empty %}<p class="mut">Keine Einträge.</p>{% else %}<div class="dtl">{% for ln in x.lanes %}<div class="dtlr"><span class="dtln">{% if ln.link %}<a href="{{ ln.link }}">{{ ln.name }}</a>{% else %}{{ ln.name }}{% endif %}</span><span class="dtlt">{% for t in x.ticks %}<u style="left:{{ t.left }}%"></u>{% endfor %}{% for b in ln.bars %}<a {% if b.link %}href="{{ b.link }}"{% endif %} class="{{ 'ov' if b.overlap }}" style="left:{{ b.left }}%;width:{{ b.width }}%;background:{{ b.color }}" title="{{ b.title }}"></a>{% endfor %}</span></div>{% endfor %}
<div class="dtlr"><span class="dtln"></span><span class="dtlx mut">{% for t in x.ticks %}<small style="left:{{ t.left }}%">{{ t.label }}</small>{% endfor %}</span></div></div>
<p class="mut" style="margin:6px 0 0"><small>{{ x.overlap_text }}: <b class="{{ 'fehler' if x.overlaps }}">{{ x.overlaps }}</b></small></p>{% endif %}
{% elif x.view == "ampel" %}<div class="damp"><span class="dot big {{ x.overall }}"></span><span>{% for k, n in x.counts.items() %}<span class="dot {{ k }}"></span> {{ n }} &nbsp;{% endfor %}{% if not x.counts %}<span class="mut">Keine Einträge.</span>{% endif %}</span></div>
{% for l in x.lights %}<div class="dlight">{% if l.link %}<a href="{{ l.link }}">{% endif %}<span class="dot {{ l.state }}"></span> <b>{{ l.label }}</b>{% if l.link %}</a>{% endif %} <small class="mut">{{ l.text }}</small></div>{% endfor %}
{% endif %}</div><span class="dres" title="Ziehen, um Breite und Höhe zu ändern"></span></section>{% endfor %}""",
"dashboard.html": r"""{% extends "base.html" %}{% block title %}Dashboard{% endblock %}
{% block actions %}<button type="button" class="btn" id="dEditBtn" onclick="dEdit(true)">Anpassen</button>{% endblock %}
{% block body %}<style>
.dgrid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));grid-auto-rows:40px;grid-auto-flow:row dense;gap:14px}
.dtile{background:var(--card);border:1px solid var(--bd);border-radius:12px;box-shadow:var(--shadow);min-width:0;min-height:0;display:flex;flex-direction:column;position:relative;overflow:hidden}
.dhead{display:flex;align-items:center;gap:8px;padding:12px 16px 4px;flex:none}.dhead h3{margin:0;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dbody{padding:4px 16px 14px;overflow:auto;flex:1;min-height:0}.dbody table{width:100%}.dbody td,.dbody th{padding:5px 6px}
.dgrip,.dedit{display:none}.dgrid.editing .dgrip{display:inline;cursor:grab;color:var(--mut)}.dgrid.editing .dedit{display:inline-flex;gap:4px;align-items:center}
.dgrid.editing .dtile{outline:2px dashed var(--bd2);outline-offset:-2px}.dgrid.editing .dtile.drag{opacity:.4}
.dres{display:none;position:absolute;right:0;bottom:0;width:22px;height:22px;cursor:nwse-resize;touch-action:none;background:linear-gradient(135deg,transparent 50%,var(--acc) 50%);border-bottom-right-radius:12px}
.dgrid.editing .dres{display:block}.dgrid.editing .dtile.rs{outline-color:var(--acc)}.dsz{min-width:44px;text-align:right}
.dnums{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px}.dnums a{display:flex;flex-direction:column;padding:8px 10px;border:1px solid var(--bd);border-radius:10px;color:inherit;text-decoration:none}
.dnums a[href]:hover{background:var(--acc-soft)}.dnums b{font-size:24px;line-height:1.2}.dnums span{color:var(--mut);font-size:12px}
.dbarrow{display:grid;grid-template-columns:minmax(80px,38%) 1fr auto;gap:10px;align-items:center;padding:4px 0}.dbl{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dbt{height:10px;background:var(--bd);border-radius:5px;overflow:hidden}.dbt i{display:block;height:100%;background:var(--acc)}.dbt i.ok{background:var(--ok)}.dbt i.fehler,.dbt i.fail{background:var(--err)}.dbt i.gestoppt,.dbt i.paused{background:var(--warn)}.dbt i.laeuft{background:var(--run)}
.dbv{white-space:nowrap;font-variant-numeric:tabular-nums}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;background:var(--bd2);vertical-align:middle}.dot.big{width:34px;height:34px}
.dot.green{background:var(--ok)}.dot.red{background:var(--err)}.dot.yellow{background:var(--warn)}.dot.blue{background:var(--run)}.dot.grey{background:var(--bd2)}
.dpies{display:flex;flex-direction:column;gap:12px}.dpt{display:block;margin-bottom:4px}.dpw{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.dpc{width:120px;height:120px;border-radius:50%;flex:none;display:grid;place-items:center;position:relative}.dpc::after{content:"";position:absolute;inset:26%;border-radius:50%;background:var(--card)}
.dpc span{position:relative;z-index:1;font-weight:700;font-size:18px}.dpl{display:flex;flex-direction:column;gap:3px;min-width:0}.dpl i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:middle}
.dspk{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;align-items:center}.dspk div{display:flex;flex-direction:column}.dspk b{font-size:28px;line-height:1.1}.dspk div span{color:var(--mut);font-size:12px}
.dspk svg{width:100%;height:44px}.dspk small{grid-column:1/-1}
.dchart{position:relative;display:flex;flex-direction:column;height:calc(100% - 26px);min-height:90px}.dchart svg{flex:1;width:100%;min-height:60px;border-bottom:1px solid var(--bd)}.dymax{font-size:11px}
.dxl{display:flex;justify-content:space-between;font-size:11px;padding-top:3px}.dleg{display:flex;gap:4px 14px;flex-wrap:wrap;margin-top:6px;font-size:13px;align-items:center}.dleg i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:middle}
.dstk{flex:1;display:flex;align-items:flex-end;gap:2px;border-bottom:1px solid var(--bd);min-height:60px}.dstc{flex:1;height:100%;display:flex;align-items:flex-end;min-width:0}.dstc>div{width:100%;display:flex;flex-direction:column-reverse;border-radius:3px 3px 0 0;overflow:hidden}
.dstc i{display:block;width:100%}.dstc:hover{background:var(--card2)}.dstx{display:flex;gap:2px;font-size:11px;padding-top:3px}.dstx span{flex:1;min-width:0;white-space:nowrap;overflow:visible}
.dgauges{display:flex;flex-wrap:wrap;gap:10px 18px}.dgauge{display:flex;flex-direction:column;align-items:center;min-width:130px;flex:1;text-align:center}.dgauge svg{width:100%;max-width:200px}
.dgauge text{font-size:17px;font-weight:700;fill:var(--fg)}.dgauge .gok{stroke:var(--ok)}.dgauge .gwarn{stroke:var(--warn)}.dgauge .gfehler{stroke:var(--err)}.dgauge small{font-size:12px}
.dheat{display:grid;grid-template-rows:repeat(7,12px);grid-auto-flow:column;gap:3px;overflow-x:auto;padding-bottom:4px}.dheat i,.dleg i.hnone{width:12px;height:12px;border-radius:3px;display:block}.dleg i[class^=h]{display:inline-block}
.dheat i.e{background:transparent}.hnone{background:var(--bd)}.hok{background:var(--ok)}.hfehler{background:var(--err)}.hwarn{background:var(--warn)}.hinfo{background:var(--acc)}
.dtl{display:flex;flex-direction:column;gap:4px}.dtlr{display:grid;grid-template-columns:minmax(70px,22%) 1fr;gap:10px;align-items:center}.dtln{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px}.dtln a{color:inherit}
.dtlt{position:relative;height:18px;background:var(--card2);border-radius:4px}.dtlt u{position:absolute;top:0;bottom:0;border-left:1px dashed var(--bd2)}.dtlt a{position:absolute;top:2px;bottom:2px;border-radius:3px;min-width:3px}
.dtlt a.ov{outline:2px solid var(--err);outline-offset:1px}.dtlx{position:relative;height:16px}.dtlx small{position:absolute;transform:translateX(-50%);font-size:11px;white-space:nowrap}
.damp{display:flex;gap:14px;align-items:center;margin:2px 0 8px}.dlight{padding:3px 0}.dlight a{color:inherit;text-decoration:none}
@media(max-width:820px){.dgrid{grid-template-columns:1fr;grid-auto-rows:auto}.dtile{grid-column:1/-1!important;grid-row:auto!important}.dtile .dbody{max-height:420px}.dres,.dsz{display:none!important}}
#dbar{display:none;margin-bottom:14px}#dbar.on{display:block}
.dtabs{display:flex;gap:4px;flex-wrap:wrap;border-bottom:1px solid var(--bd);margin:0 0 14px;align-items:flex-end}.dtabs a{padding:8px 14px;border:1px solid transparent;border-bottom:0;border-radius:10px 10px 0 0;color:var(--mut);text-decoration:none;margin-bottom:-1px;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dtabs a:hover{color:var(--fg);background:var(--card2)}.dtabs a.on{background:var(--card);border-color:var(--bd);color:var(--fg);font-weight:600}
.dtabtools{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:10px;padding-top:10px;border-top:1px solid var(--bd)}.dtabtools input{width:220px}.dadd{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center}
#dlg{width:min(860px,96vw);border:1px solid var(--bd);border-radius:12px;background:var(--card);color:var(--fg);padding:20px 22px}#dlg .dfl{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px 16px}
#dlg .dviews{display:flex;gap:6px;flex-wrap:wrap}#dlg .dviews label{display:inline-flex;gap:6px;align-items:center;border:1px solid var(--bd2);border-radius:8px;padding:5px 10px;margin:0;cursor:pointer}
#dlg .dviews label.dis{opacity:.4;cursor:not-allowed}#dlg .djobs{max-height:150px;overflow:auto;border:1px solid var(--bd);border-radius:8px;padding:6px 8px}
#dprev{margin-top:12px;display:grid;grid-template-columns:1fr;grid-auto-rows:auto}#dprev .dtile{min-height:120px;max-height:360px}#dprev .dres,#dprev .dedit,#dprev .dgrip{display:none!important}
</style>
<div class="card" id="dbar"><b>Dashboard anpassen</b> <span class="mut">Kacheln ziehen oder mit ↑ ↓ verschieben, an der Ecke unten rechts größer oder kleiner ziehen, mit ✎ die Bausteine ändern, mit ✕ ausblenden. Kleine Kacheln rücken automatisch in freie Lücken.</span>
<div class="dtabtools"><b>Tab</b><input type="text" id="tabName" maxlength="40" value="{{ tab.name }}" aria-label="Name des Tabs"><button type="button" class="btn sm" onclick="tabMove(-1)" title="Tab nach links">←</button><button type="button" class="btn sm" onclick="tabMove(1)" title="Tab nach rechts">→</button><button type="button" class="btn sm" onclick="tabNew()">+ Neuer Tab</button>{% if tabs|length > 1 %}<button type="button" class="btn sm del" onclick="tabDel()">Tab löschen</button>{% endif %}<small class="mut">Name und Reihenfolge werden mit „Speichern“ übernommen.</small></div>
<div class="dadd"><button type="button" class="btn sm pri" onclick="dOpen(null)">+ Eigene Kachel</button><select id="dpre" style="width:auto"><option value="">+ Vorlage hinzufügen …</option></select></div>
<p style="margin:12px 0 0"><button type="button" class="btn pri" onclick="dSave()">Speichern</button> <button type="button" class="btn" onclick="location.reload()">Abbrechen</button> <button type="button" class="btn" onclick="dReset()">Standard wiederherstellen</button></p></div>
<div class="dtabs" id="dtabs" role="tablist">{% for t in tabs %}<a href="/dashboard?tab={{ t.id }}" data-id="{{ t.id }}" class="{{ 'on' if t.id == tab.id }}" onclick="try{localStorage.setItem('ms-dtab',this.dataset.id)}catch(e){}">{{ t.name }}</a>{% endfor %}</div>
<div class="dgrid" id="dgrid">{% include "dashboard_tiles.html" %}</div>
{% if not layout %}<div class="card empty" id="dempty"><p>Keine Kacheln ausgewählt. Mit „Anpassen“ Kacheln hinzufügen.</p></div>{% endif %}
<dialog id="dlg"><h2 style="margin-top:0" id="dlgTitle">Kachel bearbeiten</h2>
<div class="dfl"><div><label>Titel</label><input type="text" id="fTitle" maxlength="80" placeholder="Name der Datenquelle"></div>
<div><label>Datenquelle</label><select id="fSrc"></select><div class="hint" id="fSrcHint"></div></div></div>
<label style="margin-top:10px">Darstellung</label><div class="dviews" id="fViews"></div>
<div class="dfl" id="fFil" style="margin-top:10px"></div>
<div class="dfl" style="margin-top:10px"><div><label>Breite (1–12 Spalten)</label><input type="number" id="fW" min="1" max="12"></div><div><label>Höhe (1–24 Zeilen)</label><input type="number" id="fH" min="1" max="24"></div></div>
<label style="margin-top:12px">Vorschau</label><div id="dprev"></div>
<p style="margin:14px 0 0"><button type="button" class="btn pri" onclick="dApply()">Übernehmen</button> <button type="button" class="btn" onclick="document.getElementById('dlg').close()">Abbrechen</button></p></dialog>
<script>
const CAT={{ catalog|tojson }},JOBS={{ djobs|tojson }},TABS={{ tabs|tojson }},CUR={{ tab.id|tojson }};let editing=false,dragEl=null,cur=null;const G=document.getElementById('dgrid');
(()=>{try{const q=new URLSearchParams(location.search);if(!q.get('tab')){const t=localStorage.getItem('ms-dtab');if(t&&t!==CUR&&TABS.some(x=>x.id===t))location.replace('/dashboard?tab='+encodeURIComponent(t))}else localStorage.setItem('ms-dtab',CUR)}catch(e){}})();
function curIdx(){return TABS.findIndex(t=>t.id===CUR)}
function tabBar(){const n=document.getElementById('dtabs');n.innerHTML='';TABS.forEach(t=>{const a=document.createElement('a');a.href='/dashboard?tab='+encodeURIComponent(t.id);a.textContent=t.name;if(t.id===CUR)a.className='on';n.appendChild(a)})}
document.getElementById('tabName').addEventListener('input',e=>{TABS[curIdx()].name=e.target.value;tabBar()});
function tabMove(d){const i=curIdx(),j=i+d;if(j<0||j>=TABS.length)return;[TABS[i],TABS[j]]=[TABS[j],TABS[i]];tabBar()}
function tabSync(){if(curIdx()>=0)TABS[curIdx()].tiles=dTiles();TABS.forEach(t=>{t.name=(t.name||'').trim()||"Tab"})}
async function tabPost(go){tabSync();const r=await fetch('/dashboard/layout',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({tabs:TABS})});const j=await r.json().catch(()=>({}));
 if(!r.ok||!j.ok){alert(j.error||r.status);return}const t=j.tabs[Math.max(0,Math.min(go,j.tabs.length-1))];try{localStorage.setItem('ms-dtab',t.id)}catch(e){}location.href='/dashboard?tab='+encodeURIComponent(t.id)}
function tabNew(){TABS.push({id:'',name:"Neuer Tab",tiles:[]});tabPost(TABS.length-1)}
function tabDel(){if(TABS.length<2||!confirm("Diesen Tab mit allen Kacheln löschen?"))return;const i=curIdx();TABS.splice(i,1);tabPost(Math.max(0,i-1))}
const VNAME=Object.fromEntries(CAT.views.map(v=>[v.id,v.title])),SRC=Object.fromEntries(CAT.sources.map(s=>[s.id,s]));
function cfgOf(t){try{return JSON.parse(t.dataset.cfg)}catch(e){return {id:t.dataset.id}}}
function dTiles(){return [...G.querySelectorAll('.dtile')].map(t=>Object.assign(cfgOf(t),{w:+t.dataset.w,h:+t.dataset.h}))}
function dSet(t,w,h){t.dataset.w=w;t.dataset.h=h;t.style.gridColumn='span '+w;t.style.gridRow='span '+h;const z=t.querySelector('.dsz');if(z)z.textContent=w+' × '+h}
function dRes(t){const hd=t.querySelector('.dres');if(!hd||hd.dataset.on)return;hd.dataset.on=1;
 hd.onpointerdown=e=>{if(!editing)return;e.preventDefault();e.stopPropagation();hd.setPointerCapture(e.pointerId);t.draggable=false;t.classList.add('rs');
  const gs=getComputedStyle(G),gap=parseFloat(gs.columnGap)||14,cw=(G.clientWidth-11*gap)/12+gap,rh=40+(parseFloat(gs.rowGap)||14),x0=e.clientX,y0=e.clientY,w0=+t.dataset.w,h0=+t.dataset.h;
  hd.onpointermove=m=>dSet(t,Math.max(1,Math.min(12,Math.round(w0+(m.clientX-x0)/cw))),Math.max(1,Math.min(24,Math.round(h0+(m.clientY-y0)/rh))));
  hd.onpointerup=()=>{hd.onpointermove=null;hd.onpointerup=null;t.classList.remove('rs');t.draggable=editing}}}
function dMove(b,dir){const t=b.closest('.dtile');if(dir<0&&t.previousElementSibling)G.insertBefore(t,t.previousElementSibling);else if(dir>0&&t.nextElementSibling)G.insertBefore(t.nextElementSibling,t)}
function dHide(b){b.closest('.dtile').remove()}
function dDrag(t){t.draggable=editing;t.ondragstart=e=>{dragEl=t;t.classList.add('drag');e.dataTransfer.effectAllowed='move';try{e.dataTransfer.setData('text/plain',t.dataset.id)}catch(x){}};t.ondragend=()=>{t.classList.remove('drag');dragEl=null};
 t.ondragover=e=>{if(!dragEl||dragEl===t)return;e.preventDefault();const r=t.getBoundingClientRect(),after=(e.clientY-r.top)>r.height/2||(e.clientX-r.left)>r.width*0.66;G.insertBefore(dragEl,after?t.nextSibling:t)}}
function dPrep(t){dDrag(t);dRes(t);dSet(t,+t.dataset.w,+t.dataset.h)}
function dEdit(on){editing=on;G.classList.toggle('editing',on);document.getElementById('dbar').classList.toggle('on',on);document.getElementById('dEditBtn').style.display=on?'none':'';G.querySelectorAll('.dtile').forEach(dPrep)}
const pre=document.getElementById('dpre');CAT.presets.forEach((p,i)=>{const o=document.createElement('option');o.value=i;o.textContent=p.title+' ('+VNAME[p.view]+')';pre.appendChild(o)});
pre.onchange=()=>{if(pre.value==='')return;const p=JSON.parse(JSON.stringify(CAT.presets[+pre.value]));pre.value='';if(G.querySelector('.dtile[data-id="'+p.id+'"]'))p.id='';dPut(null,p)};
async function dRender(cfg){const r=await fetch('/dashboard?preview='+encodeURIComponent(JSON.stringify(cfg)));const tx=await r.text();if(!r.ok)return {err:tx};const b=document.createElement('div');b.innerHTML=tx;return {el:b.querySelector('.dtile')}}
async function dPut(old,cfg){const res=await dRender(cfg);if(res.err){alert(res.err.replace(/<[^>]+>/g,''));return false}const el=res.el;if(old)old.replaceWith(el);else{G.appendChild(el);const e=document.getElementById('dempty');if(e)e.remove()}dPrep(el);return true}
function opt(sel,v,l,on){const o=document.createElement('option');o.value=v;o.textContent=l;if(on)o.selected=true;sel.appendChild(o)}
function dForm(cfg){const s=document.getElementById('fSrc');s.innerHTML='';CAT.sources.forEach(x=>opt(s,x.id,x.title,x.id==cfg.source));
 const src=SRC[cfg.source]||CAT.sources[0];document.getElementById('fSrcHint').textContent=src.description;
 const vs=document.getElementById('fViews');vs.innerHTML='';CAT.views.forEach(v=>{const ok=src.views.includes(v.id),l=document.createElement('label');if(!ok)l.className='dis';
  l.innerHTML='<input type="radio" name="fView" value="'+v.id+'"'+(ok?'':' disabled')+(v.id==cfg.view?' checked':'')+'> ';l.appendChild(document.createTextNode(v.title));vs.appendChild(l)});
 if(!vs.querySelector('input:checked'))vs.querySelector('input:not([disabled])').checked=true;
 const ff=document.getElementById('fFil');ff.innerHTML='';const f=cfg.filters||{};
 src.filters.forEach(x=>{const d=document.createElement('div');const lb=document.createElement('label');lb.textContent=x.label;d.appendChild(lb);let inp;
  if(x.type=='select'){inp=document.createElement('select');x.options.forEach(o=>opt(inp,o.value,o.label,(f[x.key]||'')==o.value))}
  else if(x.type=='int'){inp=document.createElement('input');inp.type='number';inp.min=x.min;inp.max=x.max;inp.value=f[x.key]||x.default}
  else{inp=document.createElement('div');inp.className='djobs';const selj=new Set(f.jobs||[]);JOBS.forEach(j=>{const l=document.createElement('label');l.className='check';l.style.margin='0';l.innerHTML='<input type="checkbox" value="'+j.id+'"'+(selj.has(j.id)?' checked':'')+'> ';l.appendChild(document.createTextNode(j.name));inp.appendChild(l)})}
  if(x.views)d.dataset.views=x.views.join(' ');inp.dataset.key=x.key;inp.dataset.type=x.type;d.appendChild(inp);if(x.hint){const h=document.createElement('div');h.className='hint';h.textContent=x.hint;d.appendChild(h)}ff.appendChild(d)});dFilVis()}
function dFilVis(){const v=(document.querySelector('input[name=fView]:checked')||{}).value;document.querySelectorAll('#fFil>div').forEach(d=>{d.hidden=!!d.dataset.views&&!d.dataset.views.split(' ').includes(v)})}
function dRead(){const c={id:cur.cfg.id||'',title:document.getElementById('fTitle').value.trim(),source:document.getElementById('fSrc').value,
 view:(document.querySelector('input[name=fView]:checked')||{}).value,filters:{},w:+document.getElementById('fW').value||4,h:+document.getElementById('fH').value||5};
 document.querySelectorAll('#fFil [data-key]').forEach(e=>{if(e.parentNode.hidden)return;const k=e.dataset.key;if(e.dataset.type=='jobs'){const v=[...e.querySelectorAll('input:checked')].map(i=>i.value);if(v.length)c.filters[k]=v}else if(e.dataset.type=='int'){c.filters[k]=+e.value}else if(e.value)c.filters[k]=e.value});return c}
let pvT=null;function dPrev(){clearTimeout(pvT);pvT=setTimeout(async()=>{const r=await dRender(dRead());const p=document.getElementById('dprev');p.innerHTML='';if(r.err)p.innerHTML=r.err;else{r.el.style.cssText='';p.appendChild(r.el)}},250)}
function dOpen(b){const t=b?b.closest('.dtile'):null;const cfg=t?Object.assign(cfgOf(t),{w:+t.dataset.w,h:+t.dataset.h}):{id:'',title:'',source:'runs',view:'number',filters:{},w:4,h:4};cur={tile:t,cfg:cfg};
 document.getElementById('dlgTitle').textContent=t?"Kachel bearbeiten":"Eigene Kachel";document.getElementById('fTitle').value=cfg.title||'';document.getElementById('fTitle').placeholder=t?t.querySelector('h3').textContent:'';
 document.getElementById('fW').value=cfg.w;document.getElementById('fH').value=cfg.h;dForm(cfg);document.getElementById('dlg').showModal();dPrev()}
document.getElementById('dlg').addEventListener('change',e=>{if(e.target.id=='fSrc'){const c=dRead();c.filters={};c.view='';dForm(c)}if(e.target.name=='fView')dFilVis();dPrev()});
document.getElementById('dlg').addEventListener('input',e=>{if(e.target.type!='checkbox'&&e.target.type!='radio')dPrev()});
async function dApply(){const c=dRead();if(await dPut(cur.tile,c))document.getElementById('dlg').close()}
async function dPost(body){const r=await fetch('/dashboard/layout',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(body)});const j=await r.json().catch(()=>({}));if(!r.ok||!j.ok){alert(j.error||r.status);return}location.reload()}
function dSave(){tabPost(curIdx())}
function dReset(){dPost({reset:true})}
setInterval(async()=>{if(editing||document.hidden||String(getSelection())!=='')return;const tp=document.getElementById('taskpop');if(tp&&!tp.hidden)return;
 try{const r=await fetch('/dashboard?partial=1&tab='+encodeURIComponent(CUR));if(r.ok&&!editing)G.innerHTML=await r.text()}catch(e){}},5000);
</script>
{% endblock %}""",
"access.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}{% block body %}{% include "tabs.html" %}
{% if msg %}<div class="msg ok">{{ msg }}</div>{% endif %}
{% if err %}<div class="msg err">{{ err }}</div>{% endif %}
{% if off %}<div class="msg info">Der Zugriffsschutz ist per Umgebungsvariable <code>IPGUARD=off</code> abgeschaltet. Die Regeln werden gespeichert, aber nicht angewendet.</div>{% endif %}
<div class="card"><h2>Deine Verbindung</h2>
<p style="margin:0">Deine Adresse: <code>{{ my_ip }}</code> {{ my_loc.flag }} {{ my_loc.name }} ·
{% if my_verdict %}<span class="tag fehler">wäre gesperrt: {{ my_verdict[0] }}</span>{% else %}<span class="tag ok">erlaubt</span>{% endif %}</p>
{% if fwd and not trust_proxy %}<div class="msg err" style="margin:10px 0 0">Du kommst über einen Reverse-Proxy (<code>X-Forwarded-For: {{ fwd }}</code>), aber „Reverse-Proxy“ ist unter <a href="/settings/general">Allgemein</a> aus. Dann sieht MirrorSync für alle Besucher nur die Adresse des Proxys ({{ my_ip }}), und eine Sperre würde alle treffen. Bitte zuerst dort das Häkchen setzen.</div>
{% else %}<p class="hint">Hinter einem Reverse-Proxy (z. B. OPNsense/HAProxy, Nginx Proxy Manager) wirken die Sperren nur richtig, wenn unter <a href="/settings/general">Allgemein</a> „Reverse-Proxy“ eingeschaltet ist.</p>{% endif %}
<p class="hint">Schutz vor dem Aussperren: Regeln, die deine aktuelle Adresse sperren würden, werden nicht gespeichert. Der Container selbst (127.0.0.1) ist nie gesperrt. Notfall-Zurücksetzen siehe README.</p></div>

<form method="post">
<div class="card"><h2>Erlaubt-Liste</h2>
<p class="mut" style="margin-top:-4px">Ist sie leer, sind alle Adressen erlaubt. Sonst kommen nur diese Adressen, Netze und Hostnamen an MirrorSync heran. Eine Zeile pro Eintrag, Kommentar nach <code>#</code>.</p>
<textarea name="allow" rows="5" placeholder="192.168.1.0/24   # Heimnetz&#10;10.8.0.0/24      # VPN&#10;buero.example.de # Büro mit DynDNS">{{ cfg.allow|join("\n") }}</textarea>
<div class="hint">Hostnamen (FQDN, z. B. <code>buero.example.de</code>) werden bei einer Anfrage per DNS aufgelöst (IPv4 und IPv6) und die Adresse damit verglichen. Das Ergebnis gilt 5 Minuten, so passen auch DynDNS-Namen. Platzhalter wie <code>*.example.de</code> gehen nicht. Ist der DNS gerade nicht erreichbar, gilt der letzte bekannte Stand.</div>
{% if hosts %}<table style="margin-top:8px"><tr><th>Hostname</th><th>Aufgelöst</th></tr>{% for h in hosts %}<tr><td><code>{{ h.host }}</code></td><td><small>{% if h.ips %}{{ h.ips|join(", ") }}{% else %}<span class="fehler">nicht auflösbar{% if h.err %} ({{ h.err }}){% endif %}</span>{% endif %}</small></td></tr>{% endfor %}</table>{% endif %}
<p style="margin:8px 0 0"><button type="button" class="btn sm" onclick="addLan()">Nur lokales Netz erlauben (private Bereiche eintragen)</button></p>
</div>

<div class="card"><h2>Länder</h2>
<div class="row"><div><label>Regel</label><select name="country_mode">
<option value="off" {{ "selected" if cfg.country_mode == "off" }}>aus</option>
<option value="allow" {{ "selected" if cfg.country_mode == "allow" }}>nur diese Länder erlauben</option>
<option value="block" {{ "selected" if cfg.country_mode == "block" }}>diese Länder sperren</option></select></div>
<div style="flex:2"><label>Länder (ISO-Codes, mit Komma)</label><input type="text" name="countries" id="cc" value="{{ cfg.countries|join(', ') }}" placeholder="DE, AT, CH"></div></div>
<div class="chips" style="margin-top:8px">{% for code, name in countries %}<a href="#" class="chip {{ 'active' if code in cfg.countries }}" onclick="tog(this,'{{ code }}');return false">{{ code }} <span>{{ name }}</span></a>{% endfor %}</div>
<div class="hint">Das lokale Netz ist von der Länderregel immer ausgenommen. {% if geo.ok %}Länder-Datenbank: <code>{{ geo.file }}</code>{% if geo.date %} vom {{ geo.date }}{% endif %}.{% else %}<span class="fehler">Keine Länder-Datenbank geladen, die Länderregel wirkt deshalb noch nicht.</span> Laden unter <a href="/settings/general">Allgemein</a>.{% endif %} Adressen, deren Land unbekannt ist, werden nicht gesperrt.</div>
</div>

<div class="card"><h2>Automatisch sperren</h2>
<div class="row"><div><label>IP sperren nach so vielen Fehlversuchen</label><input type="text" inputmode="numeric" name="auto_attempts" value="{{ cfg.auto_attempts }}"><div class="hint">0 = aus. Zählt falsche Passwörter, 2FA-Codes und unbekannte Benutzer.</div></div>
<div><label>innerhalb von Minuten</label><input type="text" inputmode="numeric" name="auto_window" value="{{ cfg.auto_window }}"></div>
<div><label>Sperrdauer in Minuten</label><input type="text" inputmode="numeric" name="auto_minutes" value="{{ cfg.auto_minutes }}"><div class="hint">0 = dauerhaft</div></div></div>
<label class="check"><input type="checkbox" name="auto_exempt_lan" {{ "checked" if cfg.auto_exempt_lan }}> Adressen aus dem lokalen Netz nie automatisch sperren (empfohlen, damit du dich nicht selbst aussperrst)</label>
<label class="check"><input type="checkbox" name="notify" {{ "checked" if cfg.notify }}> Bei automatischer Sperre über die Standard-Benachrichtigungen informieren</label>
</div>
<p><button class="btn pri">Regeln speichern</button></p>
</form>

<div class="card"><h2>Sperrliste</h2>
<form method="post" action="/settings/access/block"><div class="row" style="align-items:flex-end">
<div style="flex:2"><label>IP-Adresse, Netz oder Hostname</label><input type="text" name="net" placeholder="1.2.3.4  oder  1.2.3.0/24  oder  facebook.com" required></div>
<div style="flex:2"><label>Notiz</label><input type="text" name="note" placeholder="optional"></div>
<div><label>Dauer</label><select name="minutes"><option value="0">dauerhaft</option><option value="60">1 Stunde</option><option value="1440">1 Tag</option><option value="10080">7 Tage</option><option value="43200">30 Tage</option></select></div>
<div style="flex:0 0 auto"><button class="btn del">Sperren</button></div></div></form>
{% if rows %}<table style="margin-top:14px"><tr><th>Adresse / Netz / Host</th><th>Notiz</th><th class="hide-sm">Seit</th><th>Bis</th><th class="hide-sm">Abgewiesen</th><th></th></tr>
{% for e in rows %}<tr><td><code>{{ e.net }}</code>{% if e.is_host %}<br><small class="mut">{% if e.ips %}→ {{ e.ips|join(", ") }}{% else %}<span class="fehler">nicht auflösbar</span>{% endif %}</small>{% endif %}</td><td><small>{{ e.note or "–" }}</small><br><small class="mut">von {{ e.by or "–" }}</small></td>
<td class="hide-sm"><small>{{ e.added }}</small></td><td><small>{{ e.until|dt if e.until else "dauerhaft" }}</small></td>
<td class="hide-sm"><small>{{ e.hits }}{% if e.last %} · zuletzt {{ e.last }}{% endif %}</small></td>
<td style="text-align:right"><form class="inline" method="post" action="/settings/access/unblock"><input type="hidden" name="net" value="{{ e.net }}"><button class="btn sm">Aufheben</button></form></td></tr>{% endfor %}</table>
{% else %}<div class="empty">Keine gesperrten Adressen.</div>{% endif %}
{% set lh = rule_hits.get("Erlaubt-Liste") %}{% set ch = rule_hits.get("Länder") %}
{% if lh or ch %}<p class="hint">Seit dem Start abgewiesen: {% if lh %}{{ lh[0] }} durch die Erlaubt-Liste{% endif %}{% if lh and ch %}, {% endif %}{% if ch %}{{ ch[0] }} durch die Länderregel{% endif %}.</p>{% endif %}
</div>
<script>
function addLan(){const t=document.querySelector('[name=allow]');const add=['10.0.0.0/8      # privat','172.16.0.0/12   # privat','192.168.0.0/16  # privat','fc00::/7        # privat IPv6'];
 const have=t.value.split('\n').map(x=>x.split('#')[0].trim());t.value=(t.value.trim()?t.value.trim()+'\n':'')+add.filter(a=>!have.includes(a.split('#')[0].trim())).join('\n')}
function tog(el,c){const i=document.getElementById('cc');let l=i.value.split(/[,\s;]+/).map(x=>x.trim().toUpperCase()).filter(Boolean);
 if(l.includes(c)){l=l.filter(x=>x!==c);el.classList.remove('active')}else{l.push(c);el.classList.add('active')}i.value=l.join(', ')}
</script>
{% endblock %}""",
}

ICONS = {'chart': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6" rx="1"/><rect x="12" y="8" width="3" height="10" rx="1"/><rect x="17" y="5" width="3" height="13" rx="1"/></svg>', 'dash': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>', 'folder': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>', 'audit': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M8 13h8M8 17h5"/></svg>', 'clock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>', 'jobs': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5"/><path d="M3 21v-5h5"/></svg>', 'storage': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01"/></svg>', 'bell': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/></svg>', 'theme': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 3v18" /><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg>', 'logout': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/></svg>', 'play': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l12.5-7.5z"/></svg>', 'plus': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>', 'gear': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>', 'lock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>'}
