#!/usr/bin/env python3
import os, re, pathlib, html, sys

def read_text_any(path):
    for enc in ("utf-8","utf-16","latin-1","cp1252"):
        try:
            return pathlib.Path(path).read_text(encoding=enc).replace(chr(227), '&mdash;')
        except Exception:
            continue
    return pathlib.Path(path).read_bytes().decode("utf-8", errors="ignore").replace(chr(227), '&mdash;')

def extract_body(s):
    m = re.search(r'(?is)<body[^>]*>(.*?)</body>', s)
    if m: return m.group(1)
    s = re.sub(r'(?is)<head[^>]*>.*?</head>', '', s)
    s = re.sub(r'(?is)<!DOCTYPE[^>]*>', '', s)
    s = re.sub(r'(?is)</?html[^>]*>', '', s)
    return s

def extract_head_styles(s):
    head = re.search(r'(?is)<head[^>]*>(.*?)</head>', s)
    head = head.group(1) if head else ""
    return "\\n\\n".join(re.findall(r'(?is)<style[^>]*>(.*?)</style>', head))

def build_single_page(limbu_html_path, output_file="limbu_single_page.html"):
    limbu_html_path=os.path.abspath(limbu_html_path)
    liste_path, dico_path, eng_path = 'liste.html', 'dico.html', 'invertkey.html'

    liste_raw, dico_raw, eng_raw = read_text_any(liste_path), read_text_any(dico_path), read_text_any(eng_path)
    liste_body, dico_body, eng_body = extract_body(liste_raw), extract_body(dico_raw), extract_body(eng_raw)

    # Clean/retarget left links
    liste_body = re.sub(r'(?is)href\s*=\s*([\'"])([^\'"]*?)#([^\'"]+)\1', r'href="#\3"', liste_body)
    liste_body = re.sub(r'(?is)\s*target\s*=\s*["\'][^"\']*["\']', '', liste_body)
    liste_body = re.sub(r'(?is)<base[^>]*>', '', liste_body)

    eng_body = re.sub(r'(?i)href\s*=\s*([\'"])([^\'"]*?)#([^\'"]+)\1', r'href="#\3"', eng_body)
    eng_body = re.sub(r'(?is)\s*target\s*=\s*["\'][^"\']*["\']', '', eng_body)
    eng_body = re.sub(r'(?is)<base[^>]*>', '', eng_body)

    # Title block (below navbar)
    t1 = "Limbu-English Dictionary of the Mewa Khola dialect"
    t2 = "Boyd Michailovsky"
    title_block = "<h2>{}</h2><p><em>{}</em></p>".format(html.escape(t1), html.escape(t2))

    dico_body_clean = re.sub(r"(?is)<(p|h1|h2|h3|center)>\s*</\1>", '', dico_body)

    base_css = """:root{--pad:12px;--bg:#f8f9fa;--border:#dee2e6;--text:#212529;--primary:#0d6efd}
*{box-sizing:border-box} html,body{margin:0;padding:0;color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}
a{color:var(--primary);text-decoration:none}a:hover{text-decoration:underline}
.container-fluid{width:100%;padding-left:var(--pad);padding-right:var(--pad)}
.navbar{background:var(--bg);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:1000}
.navbar .container-fluid{display:flex;align-items:center;justify-content:space-between;min-height:60px;position:relative}
.brand{display:flex;align-items:center;gap:10px}
.logo{height:32px;width:auto;display:block}
.brand-text{display:flex;flex-direction:column;line-height:1.1}
.brand-title,.brand-title:link,.brand-title:visited,.brand-title:hover,.brand-title:active{color:var(--text);text-decoration:none}
.brand-title{font-weight:600;font-size:1rem}
.brand-subtitle{font-size:12px;color:#6c757d;margin-top:2px}
.navbar-toggler{background:transparent;border:1px solid var(--border);border-radius:6px;padding:6px 10px;cursor:pointer}
.navbar-collapse{position:absolute;top:100%;left:0;right:0;display:none;background:#fff;border-bottom:1px solid var(--border);padding:8px 12px}
.navbar-collapse.show{display:block}
.navbar-nav{list-style:none;margin:0;padding:0;display:flex;gap:12px}
.nav-link{padding:8px;border-radius:6px;display:block}
.nav-link:hover{background:#e9ecef}
@media (min-width:768px){
  .navbar-toggler{display:none}
  .navbar-collapse{position:static;display:flex !important;padding:0;background:transparent;border:0}
  .navbar-nav{margin-left:auto}
}
.page-title{padding:12px 0;border-bottom:1px solid var(--border);background:white}
.mb-3{margin-bottom:1rem}.text-center{text-align:center}
.search-bar{display:flex;align-items:stretch;gap:8px;width:100%;margin-top:6px;}
.form-control{flex:1;padding:10px 12px;border:1px solid var(--border);border-radius:8px;outline:none;min-width:0}
.form-control:focus{border-color:var(--primary);box-shadow:0 0 0 4px rgba(13,110,253,.1)}
.btn{padding:10px 14px;border:1px solid var(--border);border-radius:8px;background:white;cursor:pointer}
.btn:hover{background:#f1f3f5}
.badge{display:inline-block;font-size:12px;padding:2px 8px;background:#e9ecef;border-radius:999px}
.layout{display:grid;grid-template-columns:160px minmax(0,1fr);gap:8px;min-width:0}
.left-pane,.right-pane{border:1px solid var(--border);border-radius:10px;background:white;min-width:0}
.left-pane{padding:8px;max-height:calc(100vh - 210px);overflow:auto}
.left-pane li { list-style-type: none; }
.right-pane{padding:12px;max-height:calc(100vh - 210px);overflow:auto}
.left-pane ul {padding: 2px;}
/* Keep two columns on most phones; shrink spacing/fonts a bit */
@media (max-width: 768px){
  :root { --pad: 8px; }

  html, body { font-size: 15px; }                /* slightly smaller base */
  .navbar .container-fluid { min-height: 52px; }

  .brand-title { font-size: 0.98rem; }
  .brand-subtitle { font-size: 11px; }

  /* Two-column grid on mobile */
  .layout{
    display: grid;
    grid-template-columns: minmax(120px, 36vw) 1fr;  /* narrow left, flexible right */
    gap: 8px;
    min-width: 0;
  }

  /* Restore fixed heights (override earlier “max-height:none”) */
  .left-pane, .right-pane{
    padding: 6px;
    max-height: calc(100vh - 180px);
    overflow: auto;
  }

  /* Compact list items in the index */
  .left-pane { font-size: 0.92rem; line-height: 1.25; }
  .left-pane a { padding: 1px 3px; }
  .left-pane li { list-style-type: none; padding: 0; margin: 0; }

  /* Slightly smaller right pane text for fit */
  .right-pane { font-size: 0.96rem; line-height: 1.35; }

  /* Compact controls */
  .search-bar { gap: 6px; }
  .form-control { padding: 8px 10px; }
  .btn { padding: 8px 10px; }
}
/* Ultra-narrow devices: gracefully fall back to stacked layout */
@media (max-width: 360px){
  .layout { grid-template-columns: 1fr; }
  .left-pane { order: 2; }   /* show entries first when stacked */
  .right-pane { order: 1; }
}
.left-pane a{display:block;padding:2px 4px;border-radius:6px}
.left-pane a:hover{background:#f8f9fa}
mark.hl{background:#ffe58f;padding:0;border-radius:2px}
section{scroll-margin-top:70px}
#rightPane .flash{outline:2px dashed var(--primary);outline-offset:2px}
.panel{display:none;border:1px solid var(--border);border-radius:10px;background:white;padding:16px}
.panel .panel-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
.panel .back{border:1px solid var(--border);background:white;border-radius:8px;padding:8px 12px;cursor:pointer}
.panel.visible{display:block}"""
    inline_js = """(function(){
  function $(s,r){return (r||document).querySelector(s)}
  function $all(s,r){return Array.from((r||document).querySelectorAll(s))}
  var navPanel = $('#navbarNav'); var toggler = document.querySelector('.navbar-toggler');
  document.addEventListener('click', function(e){
    var t = e.target.closest('.navbar-toggler'); if(!t) return;
    e.preventDefault(); navPanel.classList.toggle('show'); t.setAttribute('aria-expanded', navPanel.classList.contains('show')?'true':'false');
  });
  document.addEventListener('click', function(e){
    if(!navPanel.classList.contains('show')) return;
    if(e.target.closest('#navbarNav .nav-link')){ navPanel.classList.remove('show'); if(toggler) toggler.setAttribute('aria-expanded','false'); return; }
    if(!e.target.closest('.navbar')){ navPanel.classList.remove('show'); if(toggler) toggler.setAttribute('aria-expanded','false'); }
  });
  var layout=$('.layout'), aboutPanel=$('#aboutPanel'), creditsPanel=$('#creditsPanel');
  function showPanel(p){ if(p){p.classList.add('visible');} if(layout){layout.style.display='none';} window.scrollTo({top:0,behavior:'smooth'}); }
  function hidePanels(){ if(aboutPanel)aboutPanel.classList.remove('visible'); if(creditsPanel)creditsPanel.classList.remove('visible'); if(layout){layout.style.display='';} window.scrollTo({top:0,behavior:'smooth'}); }
  function panelVisible(p){ return p&&p.classList.contains('visible'); }
  document.addEventListener('click', function(e){
    var a=e.target.closest('a.nav-link'); if(!a) return; var href=a.getAttribute('href');
    if(href==='#about'){ e.preventDefault(); if(panelVisible(aboutPanel)) hidePanels(); else { hidePanels(); showPanel(aboutPanel);} }
    else if(href==='#credits'){ e.preventDefault(); if(panelVisible(creditsPanel)) hidePanels(); else { hidePanels(); showPanel(creditsPanel);} }
  });
  document.addEventListener('click', function(e){ if(e.target.closest('.back')){ e.preventDefault(); hidePanels(); } });
  var leftPane=$('#leftPane'), rightPane=$('#rightPane');
  var esc=(window.CSS&&CSS.escape)?CSS.escape:function(s){return (s||'').replace(/[^a-zA-Z0-9_\-]/g,'\\$&');};
  function scrollToAnchor(id){
    if(!id) return;
    var t= rightPane.querySelector('[id="'+esc(id)+'"]') || rightPane.querySelector('a[name="'+esc(id)+'"]');
    if(!t) return;
    var f=(t.tagName==='A' && !t.id)?(t.nextElementSibling||t.parentElement||t):t;
    var cR=rightPane.getBoundingClientRect(), tR=f.getBoundingClientRect();
    var top=(tR.top-cR.top)+rightPane.scrollTop-8;
    rightPane.scrollTo({top:Math.max(0,top), behavior:'smooth'});
    $all('#rightPane .flash').forEach(function(n){n.classList.remove('flash');});
    f.classList.add('flash'); setTimeout(function(){f.classList.remove('flash');}, 1200);
  }
  if(leftPane){
    leftPane.addEventListener('click', function(e){
      var a=e.target.closest('a[href]'); if(!a) return;
      var href=a.getAttribute('href')||''; var m=href.match(/#(.+)$/); if(!m) return;
      e.preventDefault(); var id=decodeURIComponent(m[1]);
      scrollToAnchor(id);
      if(history&&history.replaceState){ history.replaceState(null,'','#'+id); }
    });
  }
  if(location.hash&&location.hash.length>1){ var id=decodeURIComponent(location.hash.slice(1)); setTimeout(function(){ scrollToAnchor(id); },0); }
  var searchInput=$('#searchInput'), resetBtn=$('#resetBtn'), matchCount=$('#matchCount');
  var searchScope=$('.layout'); var DEBOUNCE_MS=200, MAX_MARKS=800, MIN_LEN=2;
  function debounce(fn,ms){ var t=null; return function(){ var a=arguments,c=this; clearTimeout(t); t=setTimeout(function(){ fn.apply(c,a); }, ms); }; }
  function clearHighlights(root){ $all('mark.hl',root).forEach(function(m){ var p=m.parentNode; while(m.firstChild){ p.insertBefore(m.firstChild,m);} p.removeChild(m); }); }
  function getTextNodes(root){ var w=document.createTreeWalker(root, NodeFilter.SHOW_TEXT,{acceptNode:function(n){ if(!n.nodeValue.trim()) return NodeFilter.FILTER_REJECT; if(n.parentNode&&/^(SCRIPT|STYLE)$/i.test(n.parentNode.tagName)) return NodeFilter.FILTER_REJECT; return NodeFilter.FILTER_ACCEPT; }}); var nodes=[],n; while(n=w.nextNode()){ nodes.push(n); } return nodes; }
  function highlightAll(root, needle){
    clearHighlights(root);
    if(!needle){ matchCount.textContent=''; return; }
    if(needle.length<MIN_LEN){ matchCount.textContent='Type '+MIN_LEN+'+ characters'; return; }
    var nodes=getTextNodes(root), parts=nodes.map(function(n){return n.nodeValue;}), fullLower=parts.join('').toLowerCase(), nLower=needle.toLowerCase();
    var matches=[], idx=0; while(true){ idx=fullLower.indexOf(nLower, idx); if(idx===-1) break; matches.push([idx, idx+nLower.length]); if(matches.length>MAX_MARKS){ break; } idx+=nLower.length; }
    if(matches.length===0){ matchCount.textContent='No matches'; return; }
    var cum=[],acc=0; for(var i=0;i<parts.length;i++){ cum.push(acc); acc+=parts[i].length; }
    function locate(off){ var lo=0,hi=cum.length-1,mid; while(lo<=hi){ mid=(lo+hi)>>1; if(cum[mid]<=off){ if(mid===cum.length-1||cum[mid+1]>off) return [nodes[mid], off-cum[mid]]; lo=mid+1;} else {hi=mid-1;} } return [nodes[nodes.length-1], nodes[nodes.length-1].nodeValue.length]; }
    for(var m=Math.min(matches.length,MAX_MARKS)-1; m>=0; m--){ var s=matches[m][0], e=matches[m][1]; var sL=locate(s), eL=locate(e); var r=document.createRange(); r.setStart(sL[0], sL[1]); r.setEnd(eL[0], eL[1]); var mark=document.createElement('mark'); mark.className='hl'; try{ var frag=r.extractContents(); mark.appendChild(frag); r.insertNode(mark); }catch(err){} }
    var first=$('mark.hl',root); if(first){ first.scrollIntoView({behavior:'smooth', block:'center'}); }
    var capped=matches.length>MAX_MARKS? (MAX_MARKS+'+') : (''+matches.length);
    matchCount.textContent = capped + ' match' + (matches.length!==1?'es':'');
  }
  var runSearch=debounce(function(){ highlightAll(searchScope,(searchInput.value||'').trim()); }, DEBOUNCE_MS);
  if(searchInput){ searchInput.addEventListener('input', runSearch); searchInput.addEventListener('keydown', function(e){ if(e.key==='Escape'){ this.value=''; runSearch(); } }); }
  if(resetBtn){ resetBtn.addEventListener('click', function(){ searchInput.value=''; runSearch(); window.scrollTo({top:0, behavior:'smooth'}); }); }
})();"""

    original_css = extract_head_styles(liste_raw) + ("\\n\\n" if extract_head_styles(liste_raw) and extract_head_styles(dico_raw) else "") + extract_head_styles(dico_raw)

    final_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Limbu-English Dictionary (single page)</title>
  <style>{base_css}</style>
  {original_style}
</head>
<body>
<nav class="navbar">
  <div class="container-fluid">
    <div class="brand">
      <img class="logo" src="kirat_flag.png" alt="Logo">
      <div class="brand-text">
        <a class="brand-title" href="#">Limbu-English Dictionary</a>
        <div class="brand-subtitle">of the Mewa Khola dialect</div>
      </div>
    </div>
    <button class="navbar-toggler" type="button" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span>☰</span>
    </button>
    <div class="navbar-collapse" id="navbarNav">
      <ul class="navbar-nav">
        <li class="nav-item"><a class="nav-link" href="#about">About</a></li>
        <li class="nav-item"><a class="nav-link" href="#credits">Credits</a></li>
      </ul>
    </div>
  </div>
</nav>

<div class="container-fluid mb-3">
  <div class="search-bar">
    <input id="searchInput" class="form-control" type="text" placeholder="Search within page…" aria-label="Search">
    <button id="resetBtn" class="btn" type="button" title="Clear search">Reset</button>
    <span id="matchCount" class="badge" style="align-self:center;"></span>
  </div>
</div>

<div id="contentRoot" class="container-fluid">
  <div class="layout">
    <aside class="left-pane" id="leftPane">
      <div id="liste">
        {liste_body}
      </div>
      <div id="english">
        {eng_body}
      </div>
    </aside>
    <main class="right-pane" id="rightPane">
      {dico_body_clean}
    </main>
  </div>

  <div id="aboutPanel" class="panel">
    <div class="panel-header"><h3>About</h3><button class="back">Close</button></div>
    <div class="panel-body">
      <p>A description of the dictionary, the Mewa Khola dialect, scope, and editorial principles will go here.</p>
    </div>
  </div>

  <div id="creditsPanel" class="panel">
    <div class="panel-header"><h3>Credits</h3><button class="back">Close</button></div>
    <div class="panel-body">
      <p>Written by Boyd Michailovsky, with additional (software) contributions by John B. Lowe and Pangloss staff.</p>
    </div>
  </div>
</div>

<script>{inline_js}</script>
</body>
</html>""".format_map({
        "base_css": base_css,
        "original_style": ("<style>"+original_css+"</style>") if original_css else "",
        "title_block": title_block,
        "liste_body": liste_body,
        "eng_body": eng_body,
        "dico_body_clean": dico_body_clean,
        "inline_js": inline_js
    })
    pathlib.Path(output_file).write_text(final_html, encoding="utf-8")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_limbu_single_page_v15.py /path/to/limbu.html [output_file]")
        sys.exit(1)
    limbu_html_path = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "limbu_single_page.html"
    out = build_single_page(limbu_html_path, output)
    print("Wrote:", out)
