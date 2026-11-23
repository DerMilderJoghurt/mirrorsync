TEMPLATES = {
"base.html": r"""<!doctype html>
<html lang="{{ lang_code() }}"{% if side_mini %} data-side="mini"{% endif %}><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% block title %}MirrorSync{% endblock %} · MirrorSync</title><link rel="icon" href="/static/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
{% if auto_refresh %}<meta http-equiv="refresh" content="3">{% endif %}
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
.side-foot .ver{color:var(--mut);font-size:12px;padding:6px 10px}.side-foot .ver .upd{color:var(--acc);font-weight:600;text-decoration:none}.side-foot .ver .upd:hover{text-decoration:underline}
.side-foot button,.side-foot a{all:unset;display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;color:var(--mut);cursor:pointer;font-weight:500}
.side-foot button:hover,.side-foot a:hover{background:var(--card2);color:var(--fg)}.side-foot svg{width:16px;height:16px}
.content{flex:1;min-width:0}
aside{transition:width .18s ease,flex-basis .18s ease}.brand{position:relative}.lbl{white-space:nowrap;overflow:hidden}
.sidetog{all:unset;position:absolute;right:10px;top:50%;margin-top:-17px;width:24px;height:24px;display:grid;place-items:center;border-radius:6px;color:var(--mut);cursor:pointer}
.sidetog:hover{background:var(--card2);color:var(--fg)}.sidetog svg{width:16px;height:16px;transition:transform .18s}
:root[data-side=mini] aside{width:64px;flex-basis:64px}:root[data-side=mini] aside .lbl,:root[data-side=mini] .side-foot .ver{display:none}
:root[data-side=mini] .brand{flex-direction:column;padding:18px 0 14px;gap:8px}:root[data-side=mini] .sidetog{position:static;margin:0}:root[data-side=mini] .sidetog svg{transform:rotate(180deg)}
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
.tag.laeuft{background:var(--run-soft);color:var(--run)}.tag.gestoppt{background:var(--warn-soft);color:var(--warn)}
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
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--bd);margin:-4px 0 18px;overflow-x:auto}
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

<nav class="mobile-nav"><a href="/" class="{{ 'active' if p == '/' or p.startswith('/job') }}">Aufgaben</a><a href="/schedules" class="{{ 'active' if p.startswith('/schedules') }}">Zeitpläne</a><a href="/remotes" class="{{ 'active' if p.startswith('/remotes') }}">Speicherorte</a>{% if can('files.view') %}<a href="/files" class="{{ 'active' if p.startswith('/files') }}">Dateien</a>{% endif %}{% if can('system.audit') %}<a href="/audit" class="{{ 'active' if p.startswith('/audit') }}">Audit-Log</a>{% endif %}<a href="{{ '/users' if can('users.view') else ('/settings' if can('notify.view') else ('/settings/general' if can('system.settings') else ('/settings/access' if can('system.access') else '/account'))) }}" class="{{ 'active' if p.startswith(('/settings','/users','/account','/roles')) }}">Einstellungen{% if fail_badge %} <span class="badge">{{ fail_badge }}</span>{% endif %}</a>{% if g.user %}<a href="/logout">Abmelden</a>{% endif %}</nav>
<div class="app">
<aside>
<div class="brand"><div class="logo">{{ ICON.jobs }}</div><span class="lbl">MirrorSync</span><button type="button" class="sidetog" id="sidetog" onclick="toggleSide()" title="{{ _('Seitenleiste ausklappen') if side_mini else _('Seitenleiste einklappen') }}" aria-label="{{ _('Seitenleiste ausklappen') if side_mini else _('Seitenleiste einklappen') }}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg></button></div>
<nav>
<a href="/" class="{{ 'active' if p == '/' or p.startswith('/job') }}" title="Aufgaben">{{ ICON.jobs }}<span class="lbl">Aufgaben</span></a>
<a href="/schedules" class="{{ 'active' if p.startswith('/schedules') }}" title="Zeitpläne">{{ ICON.clock }}<span class="lbl">Zeitpläne</span></a>
<a href="/remotes" class="{{ 'active' if p.startswith('/remotes') }}" title="Speicherorte">{{ ICON.storage }}<span class="lbl">Speicherorte</span></a>
{% if can('files.view') %}<a href="/files" class="{{ 'active' if p.startswith('/files') }}" title="Dateien">{{ ICON.folder }}<span class="lbl">Dateien</span></a>{% endif %}
{% if can('system.audit') %}<a href="/audit" class="{{ 'active' if p.startswith('/audit') }}" title="Audit-Log">{{ ICON.audit }}<span class="lbl">Audit-Log</span></a>{% endif %}
<a href="{{ '/users' if can('users.view') else ('/settings' if can('notify.view') else ('/settings/general' if can('system.settings') else ('/settings/access' if can('system.access') else '/account'))) }}" class="{{ 'active' if p.startswith(('/settings','/users','/account','/roles')) }}" title="Einstellungen">{{ ICON.gear }}<span class="lbl">Einstellungen</span>{% if fail_badge %}<span class="badge" title="unbestätigte Fehlversuche">{{ fail_badge }}</span>{% endif %}</a>
</nav>
<div class="side-foot">
<button type="button" onclick="toggleTheme()" title="Design wechseln">{{ ICON.theme }}<span id="themeLabel" class="lbl">Design wechseln</span></button>
{% if g.user %}<a href="/account" class="userchip" title="{{ g.user }}"><span class="avatar">{{ g.user[:1]|upper }}</span><span class="lbl"><b>{{ g.user }}</b><br><small>{{ role_name(g.role) }}</small></span></a>
<a href="/logout" title="Abmelden">{{ ICON.logout }}<span class="lbl">Abmelden</span></a>{% endif %}
<div class="ver">MirrorSync v{{ VERSION }}{% set upd_s = UPDATE() %}{% if upd_s and upd_s.update_available %}<br><a class="upd" href="{{ upd_s.url }}" target="_blank" rel="noopener" title="Neue Version verfügbar">⬆ v{{ upd_s.latest }} verfügbar</a>{% endif %}</div>
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
    return '<div class="fm-task"><div style="flex:1;min-width:0"><b>'+esc(lab)+'</b> '+esc(t.label)+'<br><small class="mut">'+esc(t.started)+(t.stats&&t.state==='läuft'?' · '+esc(t.stats):'')+'</small>'+(t.error?'<br><small style="color:var(--err)">'+esc(t.error)+'</small>':'')+'</div>'+
      '<span class="tag" style="color:'+COL[t.state]+';white-space:nowrap">'+esc(STT[t.state]||t.state)+' · '+pc+' %</span>'+
      '<div class="fm-bar" title="'+pc+' %"><i style="width:'+pc+'%;background:'+COL[t.state]+'"></i></div>'+
      (CAN_EDIT?(t.state==='läuft'?'<button type="button" class="btn sm" data-c="'+t.id+'">'+'Abbrechen'+'</button>':'<button type="button" class="btn sm" data-r="'+t.id+'">'+'Entfernen'+'</button>'):'')+'</div>'}).join(''):'<div class="mut">'+'Keine Aufträge.'+'</div>';
  document.querySelectorAll('#tasks [data-c]').forEach(x=>x.onclick=async()=>{await op('cancel',{task_id:x.dataset.c});poll()});
  document.querySelectorAll('#tasks [data-r]').forEach(x=>x.onclick=async()=>{await op('remove_tasks',{task_id:x.dataset.r});poll()});
  const cb=document.getElementById('clrtasks');if(cb)cb.style.display=d.tasks.some(t=>t.state!=='läuft')?'':'none';
  if(wasRun&&!run&&window.onTasksDone)window.onTasksDone();wasRun=run>0;
  TT=setTimeout(poll,run?800:(jr?2000:(open?3000:10000)));}
window.msPoll=()=>{wasRun=true;poll()};
window.msTasksClear=async()=>{await op('remove_tasks',{finished:true});poll()};
window.msTasksToggle=(ev)=>{if(ev)ev.stopPropagation();const p=document.getElementById('taskpop');open=p.hidden;p.hidden=!open;if(open)poll()};
document.addEventListener('click',e=>{const p=document.getElementById('taskpop');if(!p.hidden&&!p.contains(e.target)&&!e.target.closest('#taskbtn')){p.hidden=true;open=false}});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){const p=document.getElementById('taskpop');if(!p.hidden){p.hidden=true;open=false}}});
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
</script>
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
<small>{% if j.direction == "bisync" %}⇄ Zwei-Wege · {% endif %}{% if j.n_select %}☑ nur {{ j.n_select }} {{ "Eintrag" if j.n_select == 1 else "Einträge" }} · {% endif %}{% if j.n_excludes %}{{ j.n_excludes }} Ausschlüsse · {% endif %}{% if j.versioning %}Versionierung · {% endif %}{% if j.notify_summary %}🔔 {{ j.notify_summary }}{% endif %}{% if j.dry_run %} · nur Testlauf{% endif %}</small></td>
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
{% else %}<small class="mut">{{ _("keiner geplant") }}</small>{% endif %}</div></td>
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
{% if can("jobs.logs") %}<a class="btn sm" href="/job/{{ j.id }}/log">Log</a>{% endif %} <a class="btn sm" href="/job/{{ j.id }}">{{ "Bearbeiten" if can("jobs.edit") else "Ansehen" }}</a>
{% if can("jobs.delete") %}<form class="inline" method="post" action="/job/{{ j.id }}/delete" data-q="{{ _('Aufgabe „{0}“ wirklich entfernen? Die Dateien in Quelle und Ziel bleiben unberührt.', j.name) }}" onsubmit="return confirm(this.dataset.q)"><button class="btn sm del" title="Aufgabe entfernen">Entfernen</button></form>{% endif %}</td>
</tr>{% endfor %}</table>{% endif %}
</div>
{% endblock %}
""",

"job.html": r"""{% extends "base.html" %}{% block title %}{{ job.name if job_id else "Neue Aufgabe" }}{% endblock %}
{% block subtitle %}<p>{{ "Aufgabe bearbeiten" if job_id else "Neue Spiegel-Aufgabe anlegen" }}</p>{% endblock %}
{% block actions %}{% if job_id %}<a class="btn" href="/job/{{ job_id }}/log">Log</a>{% endif %}{% endblock %}
{% block body %}
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

<div class="card"><h2>Optionen</h2>
<label class="check"><input type="checkbox" name="versioning" id="vers" {{ "checked" if job.versioning }} onchange="document.getElementById('versbox').style.display=this.checked?'':'none'"> Versionierung: gelöschte und überschriebene Dateien nach <code>&lt;ziel&gt;.versions/&lt;datum&gt;</code> verschieben statt löschen</label>
<div id="versbox" class="row" style="margin:0 0 8px 26px;{{ '' if job.versioning else 'display:none' }}">
<div style="flex:0 0 220px"><label>Versionen behalten</label><input type="text" name="versions_keep" inputmode="numeric" value="{{ job.versions_keep or '' }}" placeholder="alle"><div class="hint">Anzahl Stände, z. B. 10. Leer = alle.</div></div>
<div style="flex:0 0 220px"><label>Höchstens so alt (Tage)</label><input type="text" name="versions_days" inputmode="numeric" value="{{ job.versions_days or '' }}" placeholder="unbegrenzt"><div class="hint">z. B. 30. Leer = unbegrenzt.</div></div>
<div><div class="hint" style="margin-top:28px">Jeder Lauf, der etwas überschreibt oder löscht, legt einen Stand (Ordner mit Datum) an. Nach jedem erfolgreichen Lauf werden ältere Stände entfernt.</div></div></div>
<label class="check"><input type="checkbox" name="checksum" {{ "checked" if job.checksum }}> Vergleich per Prüfsumme statt Größe + Änderungszeit (langsamer, genauer)</label>
<label class="check"><input type="checkbox" name="dry_run" {{ "checked" if job.dry_run }}> Immer nur Testlauf (nichts wird verändert)</label>
<div class="row"><div class="ow-only"><label>Max. Löschungen pro Lauf</label><input type="text" name="max_delete" value="{{ job.max_delete }}">
<div class="hint">Schutz, falls die Quelle plötzlich leer ist. Leer = kein Limit.</div></div>
<div><label>Zusätzliche rclone-Optionen</label><input type="text" name="extra_flags" value="{{ job.extra_flags }}" {{ "disabled" if not can("jobs.advanced") }} placeholder='--transfers 8'>
<div class="hint">z. B. parallele Übertragungen. Ein eigenes <code>--bwlimit</code> hier ersetzt die Einstellung „Bandbreite“.</div></div></div>
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

"log.html": r"""{% extends "base.html" %}{% block title %}{{ job.name }}{% endblock %}{% block subtitle %}<p class="path">{{ job.source }} {{ "⇄" if job.direction == "bisync" else "→" }} {{ job.dest }}</p>{% endblock %}{% block body %}
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
<h2 style="margin:0">{{ "Aktueller Lauf" if running else "Letzter Lauf" }} {% if running %}<span class="tag laeuft">läuft</span>{% endif %}</h2>
<div>{% if running %}{% if can("jobs.run") %}<form class="inline" method="post" action="/job/{{ job_id }}/stop"><button class="btn del">Stopp</button></form>{% endif %}
{% else %}{% if can("jobs.run") %}<form class="inline" method="post" action="/job/{{ job_id }}/run"><button class="btn pri">Jetzt spiegeln</button></form>{% endif %}
{% if can("jobs.dryrun") %}<form class="inline" method="post" action="/job/{{ job_id }}/run"><input type="hidden" name="dry" value="1"><button class="btn">Testlauf</button></form>{% endif %}{% endif %}
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
<td><span class="tag {{ h.status }}">{{ STATUS.get(h.status, h.status) }}</span>{% if h.dry_run %} <small>Testlauf</small>{% endif %}</td>
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
<a class="btn sm" href="/remotes/{{ r.name }}/edit">Bearbeiten</a>{% endif %}{% if can("remotes.delete") %}
<form class="inline" method="post" action="/remotes/{{ r.name }}/delete" onsubmit="return confirm('Speicherort {{ r.name }} entfernen?')"><button class="btn sm del">Entfernen</button></form>{% endif %}</td></tr>
{% endfor %}</table>{% else %}<div class="empty">Noch keine Speicherorte angelegt.</div>{% endif %}
<p class="hint" style="padding:0 10px 8px">Alle rclone-Speicherarten werden unterstützt (SMB, WebDAV, SFTP, FTP, S3, B2, Azure, Google Drive, OneDrive, Dropbox, pCloud, MEGA, crypt und rund 45 weitere).
Lokale Ordner brauchen keinen Eintrag: Sie werden in der docker-compose.yml unter <code>/data</code> eingebunden.</p>
</div>
{% endblock %}""",

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
.fm-dlg{border:1px solid var(--bd);border-radius:12px;background:var(--card);color:var(--fg);padding:18px;width:min(560px,94vw)}
.fm-dlg.big{width:min(1100px,96vw)}.fm-dlg::backdrop{background:rgba(0,0,0,.45)}
.fm-dlg textarea{width:100%;min-height:55vh;font-family:var(--mono,monospace);font-size:13px}
.fm-scroll.dropon{outline:2px dashed var(--acc);outline-offset:-2px;background:var(--acc-soft)}.fm tr.dropdir td{background:var(--acc-soft);box-shadow:inset 0 0 0 1px var(--acc)}.fm tr[draggable=true]{cursor:grab}
</style>
{% if not locations %}<div class="card"><div class="empty">Keine Speicherorte, die du sehen darfst. Unter <a href="/remotes">Speicherorte</a> anlegen.</div></div>{% else %}
<div class="card" style="padding:12px 14px"><label class="check" style="margin:0"><input type="checkbox" id="dualchk" onchange="setDual(this.checked)"> Zwei Speicherorte nebeneinander (Kopieren und Verschieben zwischen beiden)</label></div>
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
<div><label>Typ</label><select name="type" id="type" {{ "disabled" if name }} onchange="render()"></select></div></div>
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
function val(n){ if(('opt_'+n) in FORM) return FORM['opt_'+n]; return EX[n]!==undefined?String(EX[n]):''; }
function field(o){
  const w=document.createElement('div'); w.dataset.provider=o.Provider||'';
  const l=document.createElement('label'); l.textContent=(DE[o.Name]||o.Help.split('\n')[0])+(o.Required?' *':''); w.append(l);
  let i;
  const ex=o.Examples||[];
  if(o.Type==='bool'){ i=document.createElement('select'); i.append(opt('','Standard ('+(o.DefaultStr||'false')+')'),opt('true','ja'),opt('false','nein')); }
  else if(ex.length && (o.Exclusive||o.Name==='provider')){ i=document.createElement('select'); i.append(opt('','– bitte wählen –'));
    ex.forEach(e=>i.append(opt(e.Value,e.Value+(e.Help?' – '+e.Help.split('\n')[0].slice(0,80):'')))); }
  else { i=document.createElement('input'); i.type=(o.IsPassword||(o.Sensitive&&/secret|pass|_key$/.test(o.Name)))?'password':'text'; i.autocomplete='off';
    i.placeholder=o.IsPassword&&EDIT?'(unverändert)':(o.DefaultStr||'');
    if(ex.length){const id='dl_'+o.Name+Math.random().toString(36).slice(2,6);const dl=document.createElement('datalist');dl.id=id;
      ex.forEach(e=>dl.append(opt(e.Value,e.Help?e.Help.split('\n')[0]:'')));w.append(dl);i.setAttribute('list',id);} }
  i.name='opt_'+o.Name; i.value=o.IsPassword?'':val(o.Name); if(o.Required && !(o.IsPassword&&EDIT)) i.required=true;
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
  p.options.forEach(o=>(o.Advanced?A:F).append(field(o)));
  // Neuer Speicherort: Standard-Port des Typs vorausfuellen (bleibt aenderbar)
  const po=document.querySelector('#fields [name=opt_port],#adv [name=opt_port]'), pd=(p.options.find(o=>o.Name==='port')||{}).DefaultStr;
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

<p><button class="btn pri">Speichern</button></p>
<p class="hint">Zugangsdaten werden in <code>config/settings.json</code> gespeichert (nur für den Container lesbar).</p>
</fieldset></form>
{% endblock %}""",
"login.html": r"""<!doctype html>
<html lang="{{ lang_code() }}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Anmelden · MirrorSync</title><link rel="icon" href="/static/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
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
{% if mode == "setup" %}<label for="tok">Einrichtungs-Code</label><input id="tok" type="text" name="token" value="{{ token_typed or '' }}" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="XXXX-XXXX-XXXX" required autofocus style="letter-spacing:.12em;font-family:ui-monospace,monospace">
<p class="sub" style="margin:6px 0 0;font-size:12.5px">Steht im Container-Log: <code>docker logs mirrorsync</code> (oder in <code>config/setup_token</code>). Damit kann niemand sonst deinen Container übernehmen, bevor du den Admin angelegt hast.</p>{% endif %}
<label for="u">Benutzername</label><input id="u" type="text" name="user" value="{{ user }}" autocomplete="username" {{ "" if user or mode == "setup" else "autofocus" }} required>
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
<a href="/account" class="{{ 'active' if request.path.startswith('/account') }}">Mein Konto</a></div>
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
<title>MirrorSync API</title><link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{{ sw }}/swagger-ui.css">
<style>body{margin:0;background:#fff}.top{display:flex;gap:12px;align-items:center;padding:10px 18px;border-bottom:1px solid #e5e7eb;font:14px system-ui,sans-serif}
.top a{color:#4f46e5;text-decoration:none}</style></head><body>
<div class="top"><b>MirrorSync API {{ VERSION }}</b><span style="flex:1"></span><a href="/settings/api">API-Keys</a><a href="/">Zurück zur GUI</a></div>
<div id="ui"></div>
<script src="{{ sw }}/swagger-ui-bundle.js"></script>
<script>window.ui=SwaggerUIBundle({url:'/api/v1/openapi.json',dom_id:'#ui',deepLinking:true,persistAuthorization:true,tryItOutEnabled:false});</script>
</body></html>
""",
"denied.html": r"""{% extends "base.html" %}{% block title %}Keine Berechtigung{% endblock %}{% block body %}
<div class="card"><div class="empty">{{ ICON.lock }}<p style="font-size:15px;color:var(--fg)">Dafür fehlen dir die Rechte.</p>
<p>Deine Rolle ist <b>{{ role_name(g.role) }}</b>.{% if perm %} Benötigt wird das Recht „{{ perm }}“.{% endif %} Ein Admin kann die Rolle unter Einstellungen → Rollen anpassen.</p>
<p><a class="btn" href="/">Zur Übersicht</a></p></div></div>
{% endblock %}
""",
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
<td>{% if u.totp_enabled %}<span class="tag ok">aktiv</span><br><small>{{ u.backup_left }} Backup-Codes</small>{% else %}<span class="tag">aus</span>{% endif %}{% if u.n_passkeys %}<br><small>🔑 {{ u.n_passkeys }} Passkey{{ "s" if u.n_passkeys != 1 }}</small>{% endif %}</td>
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
<p style="margin-top:20px"><button class="btn pri">Speichern</button> <a class="btn" href="/users">Abbrechen</a></p>
</form>
{% endblock %}
""",
"account.html": r"""{% extends "base.html" %}{% block title %}Einstellungen{% endblock %}
{% block body %}{% if not welcome %}{% include "tabs.html" %}{% endif %}
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
<form method="post" onsubmit="return confirm('2FA wirklich ausschalten?')"><input type="hidden" name="action" value="2fa_disable"><label>2FA ausschalten</label>
<div class="row" style="flex-direction:row"><input type="password" name="password" placeholder="Passwort zur Bestätigung" required><button class="btn del" style="flex:0 0 auto">Ausschalten</button></div></form></div>
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
<form method="post" class="card"><input type="hidden" name="section" value="update"><h2>Updates</h2>
<label class="check"><input type="checkbox" name="update_check" {{ "checked" if upd.enabled }}> Nach neuen Versionen suchen</label>
{% set upd_h = upd.interval_minutes % 60 == 0 %}<div class="row" style="margin-top:8px"><div style="flex:0 0 300px"><label>Prüfen alle</label><div style="display:flex;gap:8px"><input type="number" name="update_interval_value" min="1" max="43200" value="{{ (upd.interval_minutes // 60) if upd_h else upd.interval_minutes }}" style="width:110px"><select name="update_interval_unit"><option value="min" {{ "selected" if not upd_h }}>Minuten</option><option value="h" {{ "selected" if upd_h }}>Stunden</option></select></div></div></div>
<div class="hint">Fragt im eingestellten Abstand bei GitHub nach, ob es eine neuere Version gibt, und zeigt sie unten links neben der Versionsnummer an. Übertragen wird dabei nur die eigene Versionsnummer. Erlaubt sind 5 Minuten bis 720 Stunden, Standard 1 Stunde.</div>
<p style="margin:10px 0 0"><span class="mut">Installiert:</span> <b>v{{ upd.current }}</b>{% if upd.latest %} &nbsp;·&nbsp; <span class="mut">Neueste Version:</span> <a href="{{ upd.url }}" target="_blank" rel="noopener">v{{ upd.latest }}</a>{% if upd.update_available %} <span class="tag ok">Neue Version verfügbar</span>{% elif upd.enabled %} <span class="tag">aktuell</span>{% endif %}{% endif %}</p>
{% if upd.checked %}<p class="mut" style="margin:4px 0 0"><small>Zuletzt geprüft: {{ upd.checked }}</small></p>{% endif %}
{% if upd.error %}<p style="margin:4px 0 0;color:var(--err)"><small>Fehler bei der letzten Prüfung: {{ upd.error }}</small></p>{% endif %}
<p style="margin-top:12px"><button class="btn pri">Speichern</button> <button class="btn" name="check_now" value="1">Speichern und jetzt prüfen</button></p></form>
<form method="post"><div class="card"><h2>Logs aufbewahren</h2>
<p class="mut" style="margin-top:-4px">Jeder Lauf bekommt ein eigenes Log. Ältere Läufe werden nach jedem Lauf automatisch gelöscht.</p>
<div class="row"><div><label>Läufe pro Aufgabe behalten</label><input type="text" inputmode="numeric" name="log_keep_runs" value="{{ s.log_keep_runs }}"><div class="hint">1 bis 1000</div></div>
<div><label>Höchstens so viele Tage behalten</label><input type="text" inputmode="numeric" name="log_keep_days" value="{{ s.log_keep_days }}"><div class="hint">0 = unbegrenzt. Der neueste Lauf bleibt immer erhalten.</div></div></div>
<div class="row"><div><label>Audit-Log: so viele Tage behalten</label><input type="text" inputmode="numeric" name="audit_keep_days" value="{{ s.audit_keep_days }}"><div class="hint">0 = unbegrenzt (höchstens die neuesten 20 000 Einträge).</div></div><div></div></div>
<p class="hint">Belegt zurzeit: {{ "%.1f"|format(usage / 1048576) }} MB in <code>/logs</code>.</p>
<p><button class="btn pri">Speichern</button></p></div></form>

<form method="post"><input type="hidden" name="section" value="security"><div class="card"><h2>Anmeldung und Sicherheit</h2>
<div class="row"><div><label>Konto sperren nach so vielen Fehlversuchen</label><input type="text" inputmode="numeric" name="lock_attempts" value="{{ s.lock_attempts }}"><div class="hint">0 = nie sperren. Falsches Passwort und falscher 2FA-Code zählen.</div></div>
<div><label>Sperrdauer in Minuten</label><input type="text" inputmode="numeric" name="lock_minutes" value="{{ s.lock_minutes }}"><div class="hint">0 = dauerhaft deaktivieren, bis ein Admin es wieder freigibt. Der letzte Admin wird höchstens 15 Minuten gesperrt.</div></div></div>
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

ICONS = {'folder': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>', 'audit': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/><path d="M8 13h8M8 17h5"/></svg>', 'clock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>', 'jobs': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 3v5h-5"/><path d="M3 21v-5h5"/></svg>', 'storage': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01"/></svg>', 'bell': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/></svg>', 'theme': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 3v18" /><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg>', 'logout': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/></svg>', 'play': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l12.5-7.5z"/></svg>', 'plus': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>', 'gear': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>', 'lock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>'}
