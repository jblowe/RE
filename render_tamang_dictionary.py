import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path
from html import escape
import re

# ============== helpers ==============

# Define sets
vowels = "aeiouāīūȳôêöüAEIOU"
consonants = f"^{vowels}"  # everything not a vowel

# Regex: start of string, then either vowel-sequence or consonant-sequence
pattern = re.compile(rf"^([{vowels}]+|[^{vowels}\W\d_]+)")


def first_token(word):
    word = re.sub(r'^[0-9,\-\$\?]+', '', word)
    m = pattern.match(word)
    return m.group(1)[:2] if m else ""


def esc(s: str) -> str:
    s = re.sub(r'<.*?>', '', s or '').replace('*', '')
    s = escape(s, quote=True)
    # s = re.sub(r'/(.*?)/', '<span style="background-color: lightblue">\1</span>', s)
    return s


def render_tamang(t):
    return f'<b>{t}</b>'


def render_transliteration(t):
    return f'<i>{t}</i>'


def render_cf(t):
    if t:
        # the initial blank is important
        return f' see <a href="{t[0]}">{t[0]}</a>'
    else:
        return ''


def render_2part(part):
    try:
        tamang, trans = part.split('|')
        tamang = render_tamang(tamang)
        trans = f'<i>{trans}</i>'
        return (f'{tamang}&nbsp;{trans}')
    except:
        # if the split does not work, render the whole thing as Tamang
        if '|' in part:
            print(f'split failed: {part}')
        return (render_tamang(part))


# ============== parsing ==============

TAGS_LIST = ['phr', 'gram', 'xr', 'so', 'rec', 'nb', 'nbi', 'il', 'ilold', 'enc', 'cf']


def get_text(parent, tag):
    return (parent.findtext(tag, '') or '').strip()


def collect_texts(parent, tags_list):
    out = {}
    for tag in tags_list:
        out[tag] = [(el.text or '').strip()
                    for el in parent.findall(tag)
                    if el is not None and el.text and el.text.strip()]
    return out

def parse_mode(mode_el, base_id, idx):
    """Parse a <mode> as a subentry block (kept together short+long)."""
    level = mode_el.attrib.get('level') or mode_el.attrib.get('n') or str(idx)
    m = {
        'id': f'{base_id}-m{idx}',
        'level': level,
        'dff': get_text(mode_el, 'dff'),
        'dfe': get_text(mode_el, 'dfe'),
        'nag': get_text(mode_el, 'nag'),
        'dfn': get_text(mode_el, 'dfn'),
        'sem': get_text(mode_el, 'sem'),
        # lists
        'phr': [], 'gram': [], 'xr': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [],
        'il': [], 'ilold': [], 'enc': [], 'cf': [],
    }
    lists = collect_texts(mode_el, TAGS_LIST)
    for k, v in lists.items():
        m[k] = v
    return m

def parse_entry(entry_el, i):
    e = {
        'id': entry_el.attrib.get('id', f'e{i}'),
        'hw': get_text(entry_el, 'hw'),
        'ps': get_text(entry_el, 'ps'),
        'dff': get_text(entry_el, 'dff'),
        'dfe': get_text(entry_el, 'dfe'),
        'nag': get_text(entry_el, 'nag'),
        'dfn': get_text(entry_el, 'dfn'),
        'sem': get_text(entry_el, 'sem'),
        'emp': get_text(entry_el, 'emp'),
        'ton': get_text(entry_el, 'ton'),
        # lists
        'phr': [], 'gram': [], 'xr': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [],
        'il': [], 'ilold': [], 'enc': [], 'cf': [],
        'modes': []
    }
    lists = collect_texts(entry_el, TAGS_LIST)
    for k, v in lists.items():
        e[k] = v

    for idx, mode_el in enumerate(entry_el.findall('mode'), 1):
        e['modes'].append(parse_mode(mode_el, e['id'], idx))

    return e

def parse_entries_from_file(xml_path):
    raw = Path(xml_path).read_text(encoding='utf-8')
    raw = re.sub(r'<\?xml[^>]*\?>', '', raw).strip()
    if not raw.startswith('<root>'):
        raw = f'<root>{raw}</root>'
    root = ET.fromstring(raw)

    groups = OrderedDict()  # token -> [entries] preserving input order
    for i, entry_el in enumerate(root.findall('.//entry')):
        e = parse_entry(entry_el, i)
        # uncomment the following to include hwX
        # try:
        #     hw = e['hw'] if e['hw'] else e['hwX']
        #     e['hw'] = hw
        # except:
        #     pass
        if not e['hw']:
            continue
        tok = first_token(e['hw'])
        if tok not in groups:
            groups[tok] = []
        groups[tok].append(e)
    return groups

# ============== rendering ==============

def render_lang_lines(nag, dfn, dff, dfe):
    """Return HTML lines for np/fr/en without emitting empties. np line shows nag (if any) with optional dfn."""
    lines = []
    if nag or dfn:
        np_line = f"<span class='small-caps'>nep</span> {esc(nag)}"
        if dfn:
            np_line += f" <span class='dfn'>{render_transliteration(esc(dfn))}</span>"
        lines.append(np_line)
    if dff:
        lines.append(f"<span class='small-caps'>fr&nbsp;</span> <i>{esc(dff)}</i>")
    if dfe:
        lines.append(f"<span class='small-caps'>eng</span> <i>{esc(dfe)}</i>")
    if not lines:
        return ""
    return "<br/>".join(lines)

def render_mode_header_inline(m):
    segs = []
    if m.get('nag') or m.get('dfn'):
        np_seg = f"<span class='small-caps'>np</span> {esc(m.get('nag',''))}"
        if m.get('dfn'):
            np_seg += f" <span class='dfn'>{render_transliteration(esc(m['dfn']))}</span>"
        segs.append(np_seg)
    if m.get('dff'):
        segs.append(f"<span class='small-caps'>fr</span> <i>{esc(m['dff'])}</i>")
    if m.get('dfe'):
        segs.append(f"<span class='small-caps'>en</span> <i>{esc(m['dfe'])}</i>")
    return " — ".join(segs)

def render_long_bits(d):
    parts = []
    if d.get('sem'):
        parts.append(f"<div class='mb-1'><b>semantic domain:</b> {esc(d['sem'])}</div>")
    # for cf in d.get('cf', []):
    #     parts.append(f"<div class='mb-1'><b>cf:</b> {esc(cf)}</div>")
    ils = d.get('il', []) + d.get('ilold', [])
    if ils:
        items = ''.join(f"<li>{render_2part(esc(il))}</li>" for il in ils)
        parts.append(f"<ol class='mb-2'>{items}</ol>")
    for phr in d.get('phr', []):
        parts.append(f"<div class='mb-1'><b>phr:</b> {render_2part(esc(phr))}</div>")
    for gram in d.get('gram', []):
        parts.append(f"<div class='mb-1'><b>grammar:</b> <i>{esc(gram)}</i></div>")
    for enc in d.get('enc', []):
        parts.append(f"<div class='mb-1'><b>note (enc):</b> {esc(enc)}</div>")
    for nb in d.get('nb', []):
        parts.append(f"<div class='mb-1'><b>note:</b> {esc(nb)}</div>")
    # for nbi in d.get('nbi', []):
    #     parts.append(f"<div class='mb-1'><b>note (internal):</b> {esc(nbi)}</div>")
    for xr in d.get('xr', []):
        parts.append(f"<div class='mb-1'><b>see also:</b> {render_tamang(esc(xr))}</div>")
    # for so in d.get('so', []):
    #     parts.append(f"<div class='mb-1'><b>source:</b> {esc(so)}</div>")
    for rec in d.get('rec', []):
        parts.append(f"<div class='mb-1'><b>recorded:</b> {esc(rec)}</div>")
    return ''.join(parts)

def render_mode_block(m):
    mid = m['id']
    has_level = bool(m.get('level'))
    badge_html = f"<span class='badge text-bg-secondary level'>{esc(str(m['level']))}</span>" if has_level else "&nbsp;"
    lines = render_lang_lines(m.get('nag',''), m.get('dfn',''), m.get('dff',''), m.get('dfe',''))
    short_html = ""
    if lines:
        short_html = f"""
        <div class="mode-short short" onclick="event.stopPropagation(); return toggleMode('{esc(mid)}')">
          <div class="mode-badge">{badge_html}</div>
          <div class="mode-body"><p class="mb-0 no-hang">{lines}</p></div>
        </div>"""
    long_bits = render_long_bits(m)
    long_html = f"""
      <div class="mode-long" id="{esc(mid)}-long" style="display:none;">
        <div class="mode-badge">{'&nbsp;' if has_level else '&nbsp;'}</div>
        <div class="mode-body">{long_bits}</div>
      </div>"""
    #  keep: <div class="mode-body"><div class='mode-head mb-1 no-hang'>{render_mode_header_inline(m)}</div>{long_bits}</div>
    return f"<div class='mode-block'>{short_html}{long_html}</div>"


def render_short(entry):
    ps_html = f' <i class="small-caps">{esc(entry["ps"])}</i>' if entry.get('ps') else ''
    cf_html = render_cf(entry.get('cf', None))
    hw = render_tamang(esc(entry['hw']))
    head = f"<p class='mb-0 no-hang entry-head'>{hw}{ps_html}{cf_html}</p>"
    blocks = []
    if entry.get('modes'):
        if entry.get('dff') or entry.get('dfe') or entry.get('nag') or entry.get('dfn'):
            pseudo = {
                'id': f"{entry['id']}-m0",
                'level': None,
                'nag': entry.get('nag', ''), 'dfn': entry.get('dfn', ''),
                'dff': entry.get('dff', ''), 'dfe': entry.get('dfe', ''),
                'sem': entry.get('sem', ''),
                'phr': entry.get('phr', []), 'gram': entry.get('gram', []), 'xr': entry.get('xr', []),
                'so': entry.get('so', []), 'rec': entry.get('rec', []), 'nb': entry.get('nb', []),
                'nbi': entry.get('nbi', []),
                'il': entry.get('il', []), 'ilold': entry.get('ilold', []), 'enc': entry.get('enc', []),
            }
            blocks.append(render_mode_block(pseudo))
        for m in entry['modes']:
            blocks.append(render_mode_block(m))
        body = ''.join(blocks)
    else:
        lines = render_lang_lines(entry.get('nag', ''), entry.get('dfn', ''), entry.get('dff', ''), entry.get('dfe', ''))
        body = f"<div class='mode-sub'><p class='mb-0 no-hang'>{lines}</p></div>" if lines else ""
    return f"<div class='short' onclick=\"return toggleEntry('{esc(entry['id'])}')\">{head}{body}</div>"

def render_entry_long(entry):
    has_base_defs = entry.get('dff') or entry.get('dfe') or entry.get('nag') or entry.get('dfn')
    if entry.get('modes') and has_base_defs:
        d_extras_html = ''
    else:
        d_extras_html = render_long_bits(entry)
    return d_extras_html

# ============== HTML template (inline CSS/JS) ==============

STYLE = r"""
:root{
  --font-sans: system-ui,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --header-h: 56px;
  --search-h: 56px;
  --nav-h: 38px;
}
@media (max-width:576px){
  :root{ --header-h:60px; --search-h:64px; --nav-h:44px; }
}
html,body{ font-family:var(--font-sans); -webkit-font-smoothing:antialiased; margin:0; padding:0; }
.small-caps{ font-variant-caps:small-caps; font-size:.7rem; }
.mb-0{ margin-bottom:0; }
.ms-1{ margin-left:.25rem; }
.no-hang{ text-indent:0; margin-left:0; }

/* === Fixed Top Stack (banner + search + nav) === */
.fixed-topbar{
  position:fixed; top:0; left:0; right:0; z-index:1000;
  background:#fff;
  box-shadow:0 1px 0 rgba(0,0,0,.06);
}
/* Header (saffron banner) */
.header{
  display:flex; align-items:center; gap:.75rem;
  background:#A51931; color:#fff; width:100%;
  padding:.5rem max(.75rem, env(safe-area-inset-right)) .5rem max(.75rem, env(safe-area-inset-left));
  box-sizing:border-box; min-height:var(--header-h);
}
.header .logo{ width:28px; height:28px; border-radius:4px; background:rgba(255,255,255,.3); flex:0 0 28px; }
.header .brand{ color:#fff; text-decoration:none; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

.header .page-links{ margin-left:auto; display:flex; gap:.5rem; }
.header .page-links a{ color:#fff; text-decoration:none; padding:.25rem .5rem; border-radius:.375rem; }
.header .page-links a:hover{ background:rgba(255,255,255,.18); }

/* Hamburger (CSS-only) */
.menu-toggle{ position:absolute; left:-9999px; }
.hamburger{ display:none; cursor:pointer; margin-left:auto; padding:.25rem; }
.hamburger span{ display:block; width:24px; height:2px; background:#fff; margin:5px 0; border-radius:1px; }

@media (max-width: 768px){
  .hamburger{ display:block; flex:0 0 auto; margin-left:.5rem; }
  .header .brand{ flex:1 1 auto; min-width:0; }
  .header .page-links{ display:none; position:absolute; z-index:1001; top:100%; right:0; left:0;
    background:#fff; color:#111; border:1px solid rgba(0,0,0,.1); box-shadow:0 6px 18px rgba(0,0,0,.15);
    padding:.5rem; }
  .header .page-links a{ display:block; color:#111; padding:.5rem .75rem; border-radius:.375rem; }
  .header .page-links a:hover{ background:#f2f2f2; }
  #menu-toggle:checked ~ .page-links{ display:block; }
}

/* Search + letter nav block (hidden on About/Credits) */
.searchnav{ display:none; background:#fff; border-bottom:1px solid #e5e7eb; }
#dico:target ~ .fixed-topbar .searchnav{ display:block; }

.searchbar{ display:flex; gap:.5rem; align-items:center; padding:.4rem .75rem; }
.searchbar input[type="text"]{ flex:1 1 auto; min-width:0; font-size:1rem; padding:.5rem .75rem; border:1px solid #ced4da; border-radius:.375rem; }
.searchbar button{ flex:0 0 auto; font-size:1rem; padding:.5rem .9rem; border:1px solid #ced4da; border-radius:.375rem; background:#fff; cursor:pointer; }
.searchbar button:hover{ background:#f1f3f5; }

#letter-nav{
  display:flex; flex-wrap:wrap;
  padding:.15rem; margin:0;
  background:#fff;
  border-top:1px solid #f1f3f5;
  border-bottom:1px solid #e9ecef;
  justify-content:center;
}
#letter-nav .nav-link{
  display:inline-block; font-size:1.2rem; line-height:1.1; padding: .2rem;
  color:#0d6efd; text-decoration:none; border:1px solid transparent; border-radius:9999px;
}
#letter-nav .nav-link:hover{ background:rgba(13,110,253,.08); border-color:rgba(13,110,253,.2); }
#letter-nav .nav-link.active{ color:#fff; background:#0d6efd; border-color:#0d6efd; }

/* Views sit below the fixed stack. */
#views{ padding-top: var(--header-h); }
#dico:target ~ #views{ padding-top: calc(var(--header-h) + var(--search-h) + var(--nav-h)); }

/* Page switching (About default) */
#views > *{ display:none; }
#page-about{ display:block; }
#about:target ~ #views > *{ display:none; }  #about:target ~ #views > #page-about{ display:block; }
#credits:target ~ #views > *{ display:none; } #credits:target ~ #views > #page-credits{ display:block; }
#dico:target ~ #views > *{ display:none; }    #dico:target ~ #views > #dictionary{ display:block; }
dt{font-weight: bold; font-style: italic; }

.page{ position:relative; max-width:900px; margin:0 auto 1rem; padding:1rem 1.25rem; background:#fff;
  border:1px solid #e5e7eb; border-radius:.5rem; box-shadow:0 1px 2px rgba(0,0,0,.04); }
.page .to-dico{ position:absolute; top:.75rem; right:.75rem; font-size:.9rem; padding:.35rem .7rem; background:#fff;
  border:1px solid #ced4da; border-radius:.375rem; text-decoration:none; color:inherit; }
.page .to-dico:hover{ background:#f1f3f5; }

/* entries */
.entry{ border:1px solid #e5e7eb; border-radius:.5rem; padding:.75rem; margin:.5rem 0; background:#fff; }
.entry.expanded{ background:#f7f7f7; }
.short{ cursor:pointer; }
.short:hover{ background:#f8f9fa; }

/* modes (subentries) – grid with left badge column */
.mode-block{ margin:.35rem 0 .5rem 1rem; }
.mode-short, .mode-long{ display:grid; grid-template-columns:auto 1fr; column-gap:.5rem; align-items:start; }
.mode-badge{ width:2.1em; display:flex; justify-content:center; align-items:flex-start; }
.mode-badge .badge{ min-width:1.8em; display:inline-flex; justify-content:center; }
.mode-body{ min-width:0; } /* allow text to wrap nicely */
.mode-body > p{margin-top:0; margin-bottom:0; }
.mode-short{ padding:.25rem 0; border-top:1px dashed #eee; }
.mode-short:first-child{ border-top:none; }
/* .mode-sub p.no-hang{margin: 0; text-indent: -1.25em; padding-left: 1.25em; line-height: 1.35; overflow-wrap: anywhere; } */


.mode-head .small-caps{ font-variant-caps:small-caps; }
.badge{ display:inline-flex; align-items:center; justify-content:center; padding:.15em .45em; line-height:1.15; font-size:.85em; border-radius:9999px; }
.text-bg-secondary{ background:#6c757d; color:#fff; }

/* search results */
#search-results mark{ background:#fff3cd; padding:0 .1em; }
#search-results .long, #search-results .mode-long{ display:none; }

/* mobile text sizes */
@media (max-width:576px){
  html{ font-size:18px; }
  .header{ padding-right:max(.75rem, env(safe-area-inset-right)); padding-left:max(.75rem, env(safe-area-inset-left)); }
  .header .brand{ font-size:.95rem; }
  #letter-nav .nav-link{ font-size:1.0rem; padding:.2rem; }
  .short p, .long{ font-size:.9rem; line-height:1.2; }
  /* .mode-sub p.no-hang{text-indent: -1em;  padding-left: 1em; } */
}

/* Per-definition hanging indent using fixed-width labels */
.mode-sub p,
.mode-body p{
  margin: 0;
  text-indent: 0;           /* ensure we don't inherit any hanging from elsewhere */
}

/* Make the language labels take a fixed column, forcing wrapped text to align */
.mode-sub p .small-caps,
.mode-body p .small-caps{
  display: inline-block;
  min-width: 2.4em;         /* tunes the hanging width; 2.2–2.6em works well */
  text-align: left;         /* lines up 'np', 'fr', 'en' neatly */
  padding-right: .45em;     /* gutter before the gloss text */
  vertical-align: top;      /* top-align with the gloss */
}

/* Optional: keep romanization inline without breaking the alignment */
.mode-sub p .dfn,
.mode-body p .dfn{white-space: nowrap; }

/* Keep long words from overflowing in glosses */
.mode-sub p i,
.mode-body p i{overflow-wrap: anywhere; }
"""

SCRIPT = r"""
function toggleEntry(id){
  const el = document.getElementById(id + '-long');
  if(!el) return false;
  const show = (el.style.display === 'none' || el.style.display === '');
  el.style.display = show ? 'block' : 'none';
  const entry = document.getElementById(id);
  if (entry) entry.classList.toggle('expanded', show);
  return false;
}
function toggleMode(mid){
  const el = document.getElementById(mid + '-long');
  if(!el) return false;
  el.style.display = (el.style.display === 'none' || el.style.display === '') ? 'block' : 'none';
  return false;
}
function showToken(tok){
  document.querySelectorAll('.letter-section').forEach(s => s.style.display = 'none');
  const section = document.getElementById('section-' + tok);
  if (section) section.style.display = 'block';
  document.querySelectorAll('#letter-nav .nav-link').forEach(a => a.classList.remove('active'));
  const link = document.querySelector('#letter-nav .nav-link[data-token="' + tok + '"]');
  if (link) link.classList.add('active');
  const sr = document.getElementById('search-results'); if (sr) sr.style.display = 'none';
  return false;
}
function debounce(fn, ms=220){ let t; return (...args)=>{ clearTimeout(t); t=setTimeout(()=>fn(...args), ms); }; }
function highlightInElement(el, query){
  if(!el || !query) return;
  const rx = new RegExp(query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
  const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {
    acceptNode(n){ return n.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT; }
  });
  const nodes = []; while (tw.nextNode()) nodes.push(tw.currentNode);
  for (const node of nodes){
    const text = node.nodeValue; let m, last=0, found=false; const frag = document.createDocumentFragment();
    while ((m = rx.exec(text))){
      const s = m.index, e = s + m[0].length;
      if (s > last) frag.appendChild(document.createTextNode(text.slice(last, s)));
      const mark = document.createElement('mark'); mark.textContent = text.slice(s, e); frag.appendChild(mark);
      last = e; found = true;
    }
    if (found){
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice[last]));
      node.parentNode.replaceChild(frag, node);
    }
  }
}
function hideAllSections(){ document.querySelectorAll('.letter-section').forEach(s => s.style.display = 'none'); }
function resetSearch(){
  const input = document.getElementById('search-box'); if (input) input.value = '';
  const resultsDiv = document.getElementById('search-results'); if (resultsDiv) resultsDiv.style.display = 'none';
  const navBar = document.getElementById('letter-nav'); if (navBar) navBar.style.display = 'flex';
  hideAllSections();
  const first = document.querySelector('.letter-section'); if (first) first.style.display = 'block';
  document.querySelectorAll('#letter-nav .nav-link').forEach(a => a.classList.remove('active'));
  const firstLink = document.querySelector('#letter-nav .nav-link'); if (firstLink) firstLink.classList.add('active');
  return false;
}
function handleSearch(input){
  const q = (input.value || '').trim();
  const resultsDiv = document.getElementById('search-results'); if (!resultsDiv) return;
  const navBar = document.getElementById('letter-nav');
  resultsDiv.innerHTML = '';
  if (q.length === 0){ resetSearch(); return; }
  if (navBar) navBar.style.display = 'none';
  hideAllSections();
  resultsDiv.style.display = 'block';
  document.querySelectorAll('.entry').forEach(entry => {
    const shortArea = entry.querySelector('.short');
    const shortText = shortArea ? shortArea.textContent : '';
    if (shortText.toLowerCase().includes(q.toLowerCase())){
      const clone = entry.cloneNode(true);
      clone.querySelectorAll('[id]').forEach(n => n.removeAttribute('id'));
      const toHide = clone.querySelectorAll('.long, .mode-long'); toHide.forEach(n => n.style.display = 'none');
      resultsDiv.appendChild(clone);
      const shortClone = clone.querySelector('.short');
      if (shortClone) highlightInElement(shortClone, q);
    }
  });
  if (resultsDiv.children.length === 0){
    resultsDiv.innerHTML = '<p class="small">No results found.</p>';
  }
}
const debouncedSearch = debounce(handleSearch, 220);

/* Auto-close hamburger after tapping a page link */
document.addEventListener('click', e => {
  if (e.target.closest('.page-links a')) {
    const t = document.getElementById('menu-toggle');
    if (t) t.checked = false;
  }
});
(function () {
  function togglePage(target) {
    const want = '#' + target;
    // If already on that page, go back to dictionary; otherwise open it
    location.hash = (location.hash === want) ? '#dico' : want;

    // Close the hamburger menu on mobile if it's open
    const t = document.getElementById('menu-toggle');
    if (t) t.checked = false;
    return false;
  }

  // Wire up the header links (About / Credits) to toggle behavior
  const aboutLink   = document.querySelector('.page-links a[href="#about"]');
  const creditsLink = document.querySelector('.page-links a[href="#credits"], .page-links a[href="#credit"]');

  if (aboutLink) {
    aboutLink.addEventListener('click', function (e) {
      e.preventDefault();
      togglePage('about');
    });
  }
  if (creditsLink) {
    creditsLink.addEventListener('click', function (e) {
      e.preventDefault();
      togglePage('credits');
    });
  }
})();
"""

HTML_SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<style>{style}</style>
</head>
<body>

<!-- Anchors first so they can control both the fixed bar and views with CSS -->
<span id="about" aria-hidden="true"></span>
<span id="credits" aria-hidden="true"></span>
<span id="dico" aria-hidden="true"></span>

<!-- Fixed top stack: banner + search + letter nav -->
<div class="fixed-topbar">
  <header class="header">
    <div class="logo" aria-hidden="true"></div>
    <a class="brand" href="#dico">{title}</a>

    <!-- Mobile hamburger controller -->
    <input type="checkbox" id="menu-toggle" class="menu-toggle" aria-label="Toggle navigation">
    <label for="menu-toggle" class="hamburger" aria-hidden="true">
      <span></span><span></span><span></span>
    </label>

    <div class="page-links">
      <a href="#about">About</a>
      <a href="#credits">Credits</a>
    </div>
  </header>

  <div class="searchnav">
    <div class="searchbar">
      <input id="search-box" type="text" placeholder="Search entries..." oninput="debouncedSearch(this)">
      <button type="button" onclick="resetSearch()">Reset</button>
    </div>
    {letter_nav}
  </div>
</div>

<!-- Views below the fixed stack -->
<div id="views">
    <section id="page-about" class="page">
        <a class="to-dico" href="#dico">To Dictionary</a>
        <h4>About</h4>
        <p class="small">
            This is an early prototype of an online dictionary for the
            Tamang language of Nepal that works on both mobile devices
            and desktop computers. It is built as a single standalone
            HTML page: it requires a web browser but does not require a
            connection to the internet.
        </p>
        <p class="small">
            Two facilities for searching the dictionary are provided:
        </p>
        <ul>
            <li>Point-and-click searching using the ordered initial
                "letters" shown in the navigation bar.
            </li>
            <li>A "search box" that performs an instantaneous
                <i>free text</i> search of the entire dictionary.
            </li>
        </ul>
        <p></p>
        <p class="small">
            The dictionary contains 3,517 entries, and most have definitions
            in three languages: Nepali (in Devanagari with transliteration),
            French, and English.
        </p>
    </section>
    <section id="page-credits" class="page">
        <a class="to-dico" href="#dico">To Dictionary</a>
        <h4>Acknowledgements</h4>
        <dl>
            <dt>Dictionary</dt>
            <dd>the machine-readable dictionary used
                in this application is a work-in-progress by Martine Mazaudon (CNRS). The dictionary is the result of
                over 50 years of fieldwork in Nepal and careful lexicography. The original
                digital version is in
                <a href="http://www.montler.net/lexware/" target="_blank">Lexware</a> format,
                a computational dictionary tool written some 60 years ago.
            </dd>
            <dt>Software</dt>
            <dd>this "HTML only" version of the dictionary was created by a Python
                script written by John B. Lowe (UC Berkeley) with the help with ChatGPT. The CSS styling is
                based on Bootstrap 5, but the minimal CSS and Javascript needed to drive the application
                was extracted and is included inline. The page can be found on the web at
                <a href="https://projects.johnblowe.com/TamangDictionary.html">https://projects.johnblowe.com/dictionary.html</a>
            </dd>
        </dl>
        <p class="small">
            Please send comments, suggestions, indeed any feedback to
            <a href="mailto:johnblowe@gmail.com,mazaudon@gmail.com">the creators</a>. We would love to hear what you think.
        </p>
    </section>
  <!-- Dictionary view -->
  <div id="dictionary" class="page">
    <div class="dictionary-body">
      {sections}
      <div id="search-results" style="display:none;"></div>
    </div>
  </div>

</div>

<script>{script}</script>
</body>
</html>
"""

def build_letter_nav(groups):
    links = []
    first = True
    for tok in groups.keys():
        active = ' active' if first else ''
        links.append(f'<a class="nav-link{active}" data-token="{esc(tok)}" href="#" onclick="return showToken(\'{esc(tok)}\')">{esc(tok)}</a>')
        first = False
    return '<nav id="letter-nav">' + ''.join(links) + '</nav>'

def build_sections(groups):
    out = []
    first = True
    for tok, entries in groups.items():
        disp = '' if first else ' style="display:none;"'
        entry_html = []
        for e in entries:
            eid = esc(e['id'])
            short_html = render_short(e)
            long_html = render_entry_long(e)
            long_block = f"<div class='long' id='{eid}-long' style='display:none;'>{long_html}</div>" if long_html else "<div class='long' id='{eid}-long' style='display:none;'></div>"
            entry_html.append(f"<div id='{eid}' class='entry'>{short_html}{long_block}</div>")
        out.append(f"<div class='letter-section' id='section-{esc(tok)}'{disp}>" + ''.join(entry_html) + "</div>")
        first = False
    return ''.join(out)

def minify_html(s: str) -> str:
    s = re.sub(r'<!--.*?-->', '', s, flags=re.DOTALL)
    s = re.sub(r'>\s+<', '> <', s)
    return s.strip()

def render_html(groups, title):
    return HTML_SHELL.format(
        title=esc(title),
        style=STYLE,
        script=SCRIPT,
        letter_nav=build_letter_nav(groups),
        sections=build_sections(groups)
    )

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Render dictionary XML to standalone HTML (modes as subentries; Bootstrap-ish offline).")
    ap.add_argument("xml", help="Input XML file")
    ap.add_argument("-o", "--out", default="TamangDictionary.html", help="Output HTML file")
    ap.add_argument("--title", default="Tamang | Nepali – French – English Dictionary", help="Page title")
    ap.add_argument("--no-minify", action="store_true", help="Skip HTML minification")
    args = ap.parse_args()

    groups = parse_entries_from_file(args.xml)
    html = render_html(groups, args.title)
    if not args.no_minify:
        html = minify_html(html)
    Path(args.out).write_text(html, encoding="utf-8")
    print(f"✅ Wrote {args.out}")
