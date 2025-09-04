import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from html import escape
import re

# =====================
# Parsing
# =====================

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

def parse_base_entry(entry, i):
    base = {
        'id': entry.attrib.get('id', f'e{i}'),
        'hw': get_text(entry, 'hw'),
        'ps': get_text(entry, 'ps'),
        'dff': get_text(entry, 'dff'),
        'dfe': get_text(entry, 'dfe'),
        'nag': get_text(entry, 'nag'),
        'dfn': get_text(entry, 'dfn'),
        'sem': get_text(entry, 'sem'),
        'phr': [], 'gram': [], 'xr': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [],
        'il': [], 'ilold': [], 'enc': [], 'cf': [],
        'sub': []
    }
    lists = collect_texts(entry, TAGS_LIST)
    for k, v in lists.items():
        base[k] = v
    # Keep nested <sub> blocks if they exist (harmless passthrough)
    for j, sub in enumerate(entry.findall('sub')):
        sub_base = parse_base_entry(sub, f"{i}-sub{j}")
        base['sub'].append(sub_base)
    return base

def parse_mode_block(mode_el, base_id, idx):
    """Parse a <mode> as a 'subentry' (no headword repeat)."""
    level = mode_el.attrib.get('level') or mode_el.attrib.get('n') or str(idx)
    mode = {
        'id': f"{base_id}-m{idx}",
        'level': level,
        'dff': get_text(mode_el, 'dff'),
        'dfe': get_text(mode_el, 'dfe'),
        'nag': get_text(mode_el, 'nag'),
        'dfn': get_text(mode_el, 'dfn'),
        'sem': get_text(mode_el, 'sem'),
        'phr': [], 'gram': [], 'xr': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [],
        'il': [], 'ilold': [], 'enc': [], 'cf': [],
        '_is_base': False,
    }
    lists = collect_texts(mode_el, TAGS_LIST)
    for k, v in lists.items():
        mode[k] = v
    return mode

def parse_entries_from_file(xml_path):
    xml_text = Path(xml_path).read_text(encoding='utf-8')
    # Allow loose XML: remove xml decl and wrap in <root> if needed
    xml_text = re.sub(r'<\?xml[^>]*\?>', '', xml_text).strip()
    if not xml_text.startswith('<root>'):
        xml_text = f"<root>{xml_text}</root>"
    root = ET.fromstring(xml_text)

    entries_by_letter = defaultdict(list)

    for i, entry in enumerate(root.findall('.//entry')):
        base = parse_base_entry(entry, i)
        hw = base.get('hw', '')
        if not hw:
            continue

        # Collect modes as subentries of the single entry
        base_modes = []
        modes = entry.findall('mode')
        if modes:
            # If the base has its own definitions/notes/illustrations, include it first as mode 0
            if base.get('dff') or base.get('dfe') or base.get('nag') or base.get('dfn') or any(
                base.get(k) for k in ['il', 'ilold', 'phr', 'gram', 'enc', 'cf', 'xr', 'so', 'rec', 'nb', 'nbi']
            ):
                base_mode = {
                    'id': f"{base['id']}-m0",
                    'level': None,
                    'dff': base.get('dff', ''),
                    'dfe': base.get('dfe', ''),
                    'nag': base.get('nag', ''),
                    'dfn': base.get('dfn', ''),
                    'sem': base.get('sem', ''),
                    'phr': base.get('phr', []), 'gram': base.get('gram', []), 'xr': base.get('xr', []),
                    'so': base.get('so', []), 'rec': base.get('rec', []), 'nb': base.get('nb', []), 'nbi': base.get('nbi', []),
                    'il': base.get('il', []), 'ilold': base.get('ilold', []), 'enc': base.get('enc', []), 'cf': base.get('cf', []),
                    '_is_base': True,
                }
                base_modes.append(base_mode)
            for idx, mode_el in enumerate(modes, 1):
                base_modes.append(parse_mode_block(mode_el, base['id'], idx))
        base['modes'] = base_modes  # may be empty

        # Key by first alphabetic letter (ignore numeric tone prefixes)
        m = re.search(r'[A-Za-zÀ-ÿ]', hw)
        key = m.group(0).lower() if m else '?'
        entries_by_letter[key].append(base)

    return entries_by_letter

# =====================
# Rendering
# =====================

def esc(s: str) -> str:
    return escape(s or '', quote=True)

def render_mode_short(m):
    badge = f"<span class='badge text-bg-secondary level ms-1'>{esc(str(m['level']))}</span> " if m.get('level') else ""
    dfn_html = f" <span class='dfn'>{esc(m['dfn'])}</span>" if m.get('dfn') else ""
    return f"""
    <div class="mode-short">
      <p class="mb-0 no-hang">
        {badge}<span class="small-caps">np</span> {esc(m.get('nag',''))}{dfn_html}<br/>
        <span class="small-caps">fr</span> <i>{esc(m.get('dff',''))}</i><br/>
        <span class="small-caps">en</span> <i>{esc(m.get('dfe',''))}</i>
      </p>
    </div>
    """

def render_short(entry):
    head = f"<b>{esc(entry['hw'])}</b>" + (f" <i>{esc(entry['ps'])}</i>" if entry.get('ps') else "")
    if entry.get('modes'):
        modes_html = '\n'.join(render_mode_short(m) for m in entry['modes'])
        return f"""
        <div class="short" onclick="toggleEntry('{esc(entry['id'])}')">
          <p class="mb-0 no-hang">{head}</p>
          {modes_html}
        </div>
        """
    else:
        # Single entry without modes
        dfn_html = f" <span class='dfn'>{esc(entry.get('dfn',''))}</span>" if entry.get('dfn') else ""
        return f"""
        <div class="short" onclick="toggleEntry('{esc(entry['id'])}')">
          <p class="mb-0 no-hang">
            {head}<br/>
            <span class="small-caps">np</span> {esc(entry.get('nag',''))}{dfn_html}<br/>
            <span class="small-caps">fr</span> <i>{esc(entry.get('dff',''))}</i><br/>
            <span class="small-caps">en</span> <i>{esc(entry.get('dfe',''))}</i>
          </p>
        </div>
        """

def render_long_bits(d):
    bits = []
    if d.get('sem'):
        bits.append(f"<div class='mb-1'><b>Semantic domain:</b> {esc(d['sem'])}</div>")
    for cf in d.get('cf', []):
        bits.append(f"<div class='mb-1'><b>Cf.:</b> {esc(cf)}</div>")
    il_all = d.get('il', []) + d.get('ilold', [])
    if il_all:
        il_items = ''.join(f'<li><i>{esc(il)}</i></li>' for il in il_all)
        bits.append(f'<ol class="mb-2">{il_items}</ol>')
    for phr in d.get('phr', []):
        bits.append(f'<div class="mb-1"><b>Phrase:</b> <i>{esc(phr)}</i></div>')
    for gram in d.get('gram', []):
        bits.append(f'<div class="mb-1"><b>Grammar:</b> <i>{esc(gram)}</i></div>')
    for enc in d.get('enc', []):
        bits.append(f"<div class='mb-1'><b>Note (EN):</b> {esc(enc)}</div>")
    for xr in d.get('xr', []):
        bits.append(f'<div class="mb-1"><b>See also:</b> {esc(xr)}</div>')
    # for so in d.get('so', []):
    #     bits.append(f'<div class="mb-1"><b>Source:</b> {esc(so)}</div>')
    for rec in d.get('rec', []):
        bits.append(f"<div class='mb-1'><b>Recorded:</b> {esc(rec)}</div>")
    for nb in d.get('nb', []):
        bits.append(f"<div class='mb-1'><b>Note:</b> {esc(nb)}</div>")
    # for nbi in d.get('nbi', []):
    #    bits.append(f"<div class='mb-1'><b>Note (internal):</b> {esc(nbi)}</div>")
    return ''.join(bits)

def render_long(entry, indent=0):
    if not entry.get('modes'):
        return render_long_bits(entry)

    blocks = []
    for m in entry['modes']:
        dfn_html = f" <span class='dfn'>{esc(m.get('dfn',''))}</span>" if m.get('dfn') else ""
        badge = f"<span class='badge text-bg-secondary level ms-1'>{esc(str(m['level']))}</span> " if m.get('level') else ""
        header = (
            f"<div class='mode-header mb-1 no-hang'>"
            f"{badge}<span class='small-caps'>np</span> {esc(m.get('nag',''))}{dfn_html} — "
            f"<span class='small-caps'>fr</span> <i>{esc(m.get('dff',''))}</i> — "
            f"<span class='small-caps'>en</span> <i>{esc(m.get('dfe',''))}</i>"
            f"</div>"
        )
        blocks.append(
            f"<div class='mode-long' style='border-left:2px solid #ececec; padding-left:.75rem; margin-left:1rem; margin-top:.5rem;'>"
            f"{header}{render_long_bits(m)}"
            f"</div>"
        )
    return '\n'.join(blocks)

# =====================
# HTML generation (standalone; no external CSS/JS)
# =====================

STYLE_BLOCK = r"""
/* ===== 1) Base fonts & typography ===== */
:root{
  --font-sans: system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, Consolas, Menlo, monospace;
}
html, body{ font-family: var(--font-sans); -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
.small-caps{ font-variant-caps: small-caps; }
.no-hang{ text-indent: 0; margin-left: 0; }

/* ===== 2) Topbar header (mobile-first) ===== */
.topbar{
  position: sticky; top: 0; z-index: 1000;
  display: flex; align-items: center; gap: 1rem;
  background: #A51931; color: #fff;
  padding: .5rem .75rem; border-bottom: none;
}
/* Title link: white, no hover underline */
.topbar > a:first-of-type{ color:#fff; text-decoration:none; font-weight:600; }
.topbar > a:first-of-type:hover,
.topbar > a:first-of-type:focus{ text-decoration:none; }

.menu-toggle{ position:absolute; left:-9999px; }
.hamburger{ display:block; cursor:pointer; margin-left:auto; padding:.25rem; }
.hamburger span{ display:block; width:24px; height:2px; background:#fff; margin:5px 0; }

/* Navlinks — mobile dropdown (white/black) */
.navlinks{
  display:none;
  position:absolute; left:0; right:0; top:100%;
  background:#fff; color:#111;
  border:1px solid #e5e7eb;
  box-shadow:0 2px 6px rgba(0,0,0,.12);
  padding:.5rem;
  flex-direction:column; gap:0;
}
.navlinks a{ color:#111; text-decoration:none; padding:.5rem; border-radius:.375rem; }
.navlinks a:hover, .navlinks a:focus{ background:#f2f2f2; color:#111; }
.menu-toggle:checked ~ .navlinks{ display:flex; }

/* Desktop (≥768px): right-justified, transparent, white links */
@media (min-width:768px){
  .hamburger{ display:none; }
  .navlinks{
    margin-left:auto; position:static; background:transparent; border:0; box-shadow:none;
    display:flex; flex-direction:row; gap:.75rem; padding:0;
  }
  .navlinks a{ background:transparent; color:#fff; padding:.25rem .5rem; border-radius:.375rem; }
  .navlinks a:hover, .navlinks a:focus{ background:rgba(255,255,255,.18); color:#fff; }
}

/* ===== 3) Letter navbar (nav-pills) ===== */
#letter-nav{
  display:flex; flex-wrap:wrap; align-items:center; gap:.25rem; padding:.25rem;
  background:#f8f9fa; border:1px solid #e9ecef; border-radius:.5rem;
}
#letter-nav .nav-link{
  display:inline-block; padding:.25rem .5rem; font-size:.9rem; line-height:1.2;
  color:#0d6efd; text-decoration:none; border:1px solid transparent; border-radius:9999px;
  transition:background-color .15s ease, color .15s ease, border-color .15s ease, box-shadow .15s ease;
}
#letter-nav .nav-link:hover{ background:rgba(13,110,253,.08); border-color:rgba(13,110,253,.2); }
#letter-nav .nav-link.active{ color:#fff; background:#0d6efd; border-color:#0d6efd; }
#letter-nav .nav-link:focus-visible{ outline:none; box-shadow:0 0 0 .2rem rgba(13,110,253,.25); }

/* ===== 4) Search bar ===== */
.searchbar{ display:flex; align-items:stretch; gap:.5rem; width:100%; margin:.75rem 0; }
.searchbar input[type="text"]{
  flex:1 1 auto; min-width:0; font-size:1rem; padding:.5rem .75rem;
  border:1px solid #ced4da; border-radius:.375rem;
}
.searchbar button{
  flex:0 0 auto; font-size:1rem; padding:.5rem .9rem;
  border:1px solid #ced4da; border-radius:.375rem; background:#fff; cursor:pointer;
}
.searchbar button:hover{ background:#f1f3f5; }

/* ===== 5) Entries ===== */
.short{ cursor:pointer; }
.short:hover{ background:#f8f9fa; }
.entry.expanded{ background:#f7f7f7; border-color:#e2e3e5; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.04); }
#search-results .long{ display:none; }
#search-results mark{ background:#fff3cd; padding:0 .1em; }
.dfn{ margin-left:.35rem; opacity:.85; font-style:italic; }

.text-bg-secondary{ background:#6c757d; color:#fff; }
.ms-1{ margin-left:.25rem; }
.badge.level{
  display:inline-flex; align-items:center; justify-content:center;
  padding:.15em .45em; line-height:1.15; font-size:.85em; border-radius:9999px;
}

/* Mode (subentry) visuals */
.mode-short{ margin:.25rem 0 .5rem 1rem; padding-left:.5rem; border-left:2px solid #ececec; }
.mode-header .small-caps{ font-variant-caps: small-caps; }

/* ===== 6) Static pages & CSS-only view switching ===== */
.hidden{ display:none !important; }
.page-view{
  position:relative; display:block; min-height:60vh; max-width:900px; margin:1rem auto; padding:1rem 1.25rem;
  background:#fff; border:1px solid #e5e7eb; border-radius:.5rem; box-shadow:0 1px 2px rgba(0,0,0,.04);
}
.page-view .lead{ font-size:1.1rem; opacity:.9; }
.page-view .back{
  position:absolute; top:.75rem; right:.75rem; font-size:.9rem; padding:.35rem .7rem;
  background:#fff; border:1px solid #ced4da; border-radius:.375rem; cursor:pointer; text-decoration:none; color:inherit;
}
.page-view .back:hover{ background:#f1f3f5; }

/* Swap views with :target (About default) */
#views > *{ display:none; }
#views > #page-about{ display:block; }
#about:target ~ #views > *{ display:none; }         #about:target ~ #views > #page-about{ display:block; }
#credits:target ~ #views > *{ display:none; }       #credits:target ~ #views > #page-credits{ display:block; }
#dictionary:target ~ #views > *{ display:none; }    #dictionary:target ~ #views > #dictionary-view{ display:block; }
#about, #credits, #dictionary{ scroll-margin-top:72px; }

/* ===== 7) Mobile tweaks ===== */
@media (max-width:576px){
  html{ font-size:18px; }
  .topbar{ padding:.4rem .6rem; }
  .topbar > a:first-of-type{ flex:1 1 auto; min-width:0; font-size:.85rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .hamburger{ padding:.2rem; } .hamburger span{ width:22px; }
  #letter-nav{ gap:.2rem; padding:.2rem; } #letter-nav .nav-link{ font-size:1rem; padding:.35rem .6rem; }
  .short p, .long{ font-size:1.1rem; line-height:1.45; }
  .page-view{ padding:1rem; margin:.75rem auto; } .page-view .back{ top:.5rem; right:.5rem; font-size:1rem; padding:.45rem .85rem; }
}
"""

SCRIPT_BLOCK = r"""
// --- Toggle long/short for entries
function toggleEntry(id){
  const longEl = document.getElementById(id + '-long');
  const entryEl = document.getElementById(id);
  if(!longEl) return;
  const show = (longEl.style.display === 'none' || longEl.style.display === '');
  longEl.style.display = show ? 'block' : 'none';
  if (entryEl) entryEl.classList.toggle('expanded', show);
}

// --- Letter sections
function showLetter(letter){
  document.querySelectorAll('.letter-section').forEach(s => s.style.display = 'none');
  const results = document.getElementById('search-results'); if (results) results.style.display = 'none';
  const section = document.getElementById('section-' + letter); if (section) section.style.display = 'block';
  document.querySelectorAll('#letter-nav .nav-link').forEach(a => a.classList.remove('active'));
  const link = Array.from(document.querySelectorAll('#letter-nav .nav-link')).find(a => a.textContent.trim() === letter);
  if (link) link.classList.add('active');
  return false;
}

// --- Search (with optional debounce and highlighting)
function debounce(fn, ms=200){ let t; return (...args)=>{ clearTimeout(t); t=setTimeout(()=>fn(...args), ms); }; }

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
  const firstLink = document.querySelector('#letter-nav .nav-link'); if (firstLink) firstLink.classList.add('active');
  return false;
}

function handleSearch(input){
  const query = (input.value || '').trim();
  const resultsDiv = document.getElementById('search-results'); if (!resultsDiv) return;
  const navBar = document.getElementById('letter-nav');
  resultsDiv.innerHTML = '';
  if (query.length === 0){ resetSearch(); return; }
  if (navBar) navBar.style.display = 'none';
  hideAllSections();
  resultsDiv.style.display = 'block';
  document.querySelectorAll('.entry').forEach(entry => {
    const shortArea = entry.querySelector('.short');
    const shortText = shortArea ? shortArea.textContent : '';
    if (shortText.toLowerCase().includes(query.toLowerCase())){
      const clone = entry.cloneNode(true);
      // remove duplicate IDs in clones
      clone.querySelectorAll('[id]').forEach(n => n.removeAttribute('id'));
      const long = clone.querySelector('.long'); if (long) long.style.display = 'none';
      resultsDiv.appendChild(clone);
      const shortClone = clone.querySelector('.short');
      if (shortClone) highlightInElement(shortClone, query);
    }
  });
  if (resultsDiv.children.length === 0){
    resultsDiv.innerHTML = '<p class="text-muted">No results found.</p>';
  }
}

const debouncedSearch = debounce(handleSearch, 200);

// Close the mobile menu when a nav link is clicked (so the dropdown collapses)
document.addEventListener('click', function(e){
  if (e.target.closest('.navlinks a')) {
    const mt = document.getElementById('menu-toggle'); if (mt) mt.checked = false;
  }
});

// Ensure first letter shows when #dictionary is targeted on load
document.addEventListener('DOMContentLoaded', () => {
  if ((location.hash || '') === '#dictionary') {
    const first = document.querySelector('.letter-section');
    if (first) first.style.display = 'block';
    const firstLink = document.querySelector('#letter-nav .nav-link');
    if (firstLink) firstLink.classList.add('active');
  }
});
"""

def generate_html(entries_by_letter, title="Tamang | Nepali – French – English Dictionary"):
    # Build letter nav
    letters = sorted(entries_by_letter.keys())
    nav_links = ''.join(
        f'<a class="nav-link" href="#" onclick="return showLetter(\'{escape(letter)}\')">{escape(letter)}</a>'
        for letter in letters
    )
    letter_nav = f'<nav id="letter-nav">{nav_links}</nav>'

    # Build content sections
    content_divs = ''
    for letter, entries in sorted(entries_by_letter.items()):
        entry_divs = ''
        for entry in entries:
            entry_id = esc(entry['id'])
            entry_divs += (
                f'<div id="{entry_id}" class="entry">'
                f'{render_short(entry)}'
                f'<div class="long" id="{entry_id}-long" style="display:none;">'
                f'{render_long(entry)}'
                f'</div></div>'
            )
        content_divs += f'<div class="letter-section" id="section-{esc(letter)}" style="display:none;">{entry_divs}</div>'

    # HTML skeleton (standalone)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(title)}</title>
  <style>
  {STYLE_BLOCK}
  </style>
</head>
<body>

<header class="topbar">
  <a href="#dictionary">{esc(title)}</a>

  <input type="checkbox" id="menu-toggle" class="menu-toggle" aria-label="Toggle navigation">
  <label for="menu-toggle" class="hamburger" aria-hidden="true"><span></span><span></span><span></span></label>

  <nav class="navlinks">
    <a href="#about">About</a>
    <a href="#credits">Credits</a>
  </nav>
</header>

<!-- anchors that control CSS-only view switching -->
<span id="about" aria-hidden="true"></span>
<span id="credits" aria-hidden="true"></span>
<span id="dictionary" aria-hidden="true"></span>

<div id="views">

  <!-- About page (default) -->
  <section id="page-about" class="page-view">
    <a class="back" href="#dictionary">Back</a>
    <h2>About</h2>
    <p class="lead">What this dictionary is and how to use it.</p>
    <p class="no-hang">This is an offline, static HTML rendering of a multilingual dictionary. Tap a headword to expand its examples and notes. Use the letter bar or the search box to browse.</p>
  </section>

  <!-- Credits page -->
  <section id="page-credits" class="page-view">
    <a class="back" href="#dictionary">Back</a>
    <h2>Credits</h2>
    <p class="lead">Acknowledgements &amp; sources.</p>
    <ul class="no-hang">
      <li>Lexicography and corpus: …</li>
      <li>Software and tooling: …</li>
    </ul>
  </section>

  <!-- Dictionary view -->
  <div id="dictionary-view">
    <div class="searchbar">
      <input id="search-box" type="text" placeholder="Search entries..." oninput="(window.debouncedSearch || handleSearch)(this)">
      <button type="button" onclick="resetSearch()">Reset</button>
    </div>

    {letter_nav}

    {content_divs}

    <div id="search-results" style="display:none;"></div>
  </div>

</div>

<script>
{SCRIPT_BLOCK}
</script>

</body>
</html>
"""
    return html

def minify_html(s: str) -> str:
    # remove HTML comments
    s = re.sub(r"<!--.*?-->", "", s, flags=re.DOTALL)
    # collapse whitespace between tags
    s = re.sub(r">\s+<", "><", s)
    return s.strip()

# ------------- CLI -------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Render multilingual dictionary XML to standalone HTML (modes as subentries).")
    ap.add_argument("xml", nargs="?", default="chunk.xml", help="Input XML file")
    ap.add_argument("-o", "--out", default="dictionary.html", help="Output HTML file")
    ap.add_argument("--title", default="Tamang | Nepali – French – English Dictionary", help="Page title")
    args = ap.parse_args()

    entries = parse_entries_from_file(args.xml)
    html = generate_html(entries, title=args.title)
    html = minify_html(html)
    Path(args.out).write_text(html, encoding="utf-8")
    print(f"✅ Wrote {args.out}")
