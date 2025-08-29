import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from html import escape
import re

# ---------- Parsing ----------

TAGS_SIMPLE = [
    'hw', 'hwX', 'ps', 'dff', 'dfe', 'nag', 'dfn'
]
TAGS_LIST = [
    'phr', 'gram', 'xr', 'so', 'rec', 'nb', 'nbi', 'il', 'ilold', 'enc'
]

# Define sets
vowels = "aeiouāīūȳôêöüAEIOU"
consonants = f"^{vowels}"  # everything not a vowel

# Regex: start of string, then either vowel-sequence or consonant-sequence
pattern = re.compile(rf"^([{vowels}]+|[^{vowels}\W\d_]+)")

def initial_cluster(word):
    word = re.sub(r'^[0-9,\-\$\?]+', '', word)
    m = pattern.match(word)
    return m.group(1)[:2] if m else ""

def collect_texts(parent, tags_list):
    out = {}
    for tag in tags_list:
        out[tag] = [(el.text or '').strip() for el in parent.findall(tag) if el is not None and el.text]
    return out


def get_text(parent, tag):
    return (parent.findtext(tag, '') or '').strip()


def minify_html(s: str) -> str:
    # remove HTML comments
    s = re.sub(r"<!--.*?-->", "", s, flags=re.DOTALL)
    # collapse whitespace between tags: ...>   <...  ->  ><
    s = re.sub(r">\s+<", "><", s)
    # trim leading/trailing whitespace
    return s.strip()


def parse_base_entry(entry, i):
    base = {
        'id': entry.attrib.get('id', f'e{i}'),
        'hw': get_text(entry, 'hw'),
        'hwX': get_text(entry, 'hwX'),
        'ps': get_text(entry, 'ps'),
        'dff': get_text(entry, 'dff'),
        'dfe': get_text(entry, 'dfe'),
        'nag': get_text(entry, 'nag'),
        'dfn': get_text(entry, 'dfn'),
        'cf': get_text(entry, 'cf'),
        'phr': [], 'gram': [], 'xr': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [], 'il': [], 'ilold': [], 'enc': [],
        'sem': get_text(entry, 'sem'),
        'level': None,
        'sub': []
    }
    lists = collect_texts(entry, TAGS_LIST)
    for k, v in lists.items():
        base[k] = v

    for j, sub in enumerate(entry.findall('sub')):
        sub_base = parse_base_entry(sub, f"{i}-sub{j}")
        base['sub'].append(sub_base)

    return base


def apply_mode(base, mode_el, level_label, i, idx):
    sense = {k: (v[:] if isinstance(v, list) else v) for k, v in base.items()}
    sense['id'] = f"{base['id']}-m{idx}"
    sense['level'] = level_label

    for t in TAGS_SIMPLE:
        val = get_text(mode_el, t)
        if val:
            sense[t] = val

    lists = collect_texts(mode_el, TAGS_LIST)
    for k, v in lists.items():
        if v:
            sense[k] = v

    return sense


def parse_entries_from_file(xml_path):
    xml_text = Path(xml_path).read_text(encoding='utf-8')
    xml_text = re.sub(r'<\?xml[^>]*\?>', '', xml_text).strip()
    if not xml_text.startswith('<root>'):
        xml_text = f"<root>{xml_text}</root>"

    root = ET.fromstring(xml_text)
    entries_by_letter = defaultdict(list)

    for i, entry in enumerate(root.findall('.//entry')):
        base = parse_base_entry(entry, i)
        try:
            hw = base['hw'] if base['hw'] else base['hwX']
            base['hw'] = hw
        except:
            pass
        if not hw:
            continue
        # Group by initial (ignore numeric prefixes)
        key = initial_cluster(hw)

        modes = entry.findall('mode')
        if modes:
            for idx, mode_el in enumerate(modes, 1):
                level = mode_el.attrib.get('level') or mode_el.attrib.get('n') or str(idx)
                sense = apply_mode(base, mode_el, level, i, idx)
                entries_by_letter[key].append(sense)
        else:
            entries_by_letter[key].append(base)

    return entries_by_letter

# ---------- Rendering helpers ----------

def esc(s):
    return escape(s or '', quote=True)


def render_short(entry):
    level_badge = f"<span class=\"badge bg-secondary ms-1\">{esc(str(entry['level']))}</span>&nbsp;" if entry.get('level') else ''
    defs = [('fr', 'dff'), ('en', 'dfe')]
    only_if = '\n'.join(
        [f"""<span class=\"small-caps\">{x[0]}</span> {esc(entry[x[1]])}<br/>""" for x in defs if entry[x[1]] != '']
    )
    cf = f"""see <a href="">{entry['cf']}</a>""" if entry['cf'] else ''
    if cf != '':
        pass
    dfn_html = f" <span class=\"dfn\">{esc(entry['dfn'])}</span>" if entry.get('dfn') else ''
    if 'nag' in entry and entry['nag'] != '':
        nag = f"""<span class="small-caps">np</span> {esc(entry['nag'])}&nbsp;{dfn_html}<br/>"""
    else:
        nag = ''
    return f"""
    <div class=\"short\" onclick=\"toggleEntry('{esc(entry['id'])}')\">
      <p class=\"mb-0\">
        <b>{esc(entry['hw'])}</b>&nbsp;{level_badge} <i>{esc(entry['ps'])}</i><br/>
        {nag}
        {only_if}
        {cf}
      </p>
    </div>
    """


def render_long(entry, indent=0):
    pad = '  ' * indent
    blocks = []

    if entry.get('sem'):
        blocks.append(f"{pad}<div class=\"mb-1\"><b>Semantic domain:</b> {esc(entry['sem'])}</div>")

    il_all = entry.get('il', []) + entry.get('ilold', [])
    if il_all:
        il_items = ''.join(f'<li><i>{esc(il)}</i></li>' for il in il_all)
        blocks.append(f'{pad}<ol class="mb-2">{il_items}</ol>')

    for phr in entry.get('phr', []):
        blocks.append(f'{pad}<div class="mb-1"><b>Phrase:</b> <i>{esc(phr)}</i></div>')
    for gram in entry.get('gram', []):
        blocks.append(f'{pad}<div class="mb-1"><b>Grammar:</b> <i>{esc(gram)}</i></div>')
    for enc in entry.get('enc', []):
        blocks.append(f'{pad}<div class="mb-1"><b>Note (EN):</b> {esc(enc)}</div>')
    for xr in entry.get('xr', []):
        blocks.append(f'{pad}<div class="mb-1"><b>See also:</b> {esc(xr)}</div>')
    for so in entry.get('so', []):
        blocks.append(f'{pad}<div class="mb-1"><b>Source:</b> {esc(so)}</div>')
    for rec in entry.get('rec', []):
        blocks.append(f'{pad}<div class="mb-1"><b>Recorded:</b> {esc(rec)}</div>')
    for nb in entry.get('nb', []):
        blocks.append(f'{pad}<div class="mb-1"><b>Note:</b> {esc(nb)}</div>')
    for nbi in entry.get('nbi', []):
        blocks.append(f'{pad}<div class="mb-1"><b>Note (internal):</b> {esc(nbi)}</div>')

    for sub in entry.get('sub', []):
        blocks.append(
            f'{pad}<div class="ms-4 border-start ps-3 mt-3">'
            f'{render_short(sub)}'
            f'<div class="long mt-2">{render_long(sub, indent+1)}</div>'
            f'</div>'
        )

    return '\n'.join(blocks)

# ---------- Page generation ----------

def generate_html(entries_by_letter):
    nav_links = ''.join(
        f'<a class="nav-link" href="#" onclick="return showLetter(\'{escape(letter)}\')">{escape(letter)}</a>'
        for letter in entries_by_letter
    )
    nav_bar = f"""
    <nav class="nav nav-pills flex-wrap sticky-top bg-light p-2 mb-3" id="letter-nav">
        {nav_links}
    </nav>
    """

    content_divs = ''
    for letter, entries in entries_by_letter.items():
        entry_divs = ''
        for entry in entries:
            entry_id = esc(entry['id'])
            entry_divs += f'''
            <div id="{entry_id}" class="entry mb-3 p-3 rounded border">
              {render_short(entry)}
              <div class="long mt-2" id="{entry_id}-long" style="display:none;">
                {render_long(entry)}
              </div>
            </div>'''
        content_divs += f'<div class="letter-section" id="section-{esc(letter)}" style="display:none;">{entry_divs}</div>'

    style = """
/* ===== 1) Base fonts & typography ===== */
:root{
  --font-sans: system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, Consolas, Menlo, monospace;
}
html, body{
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.small-caps{
  font-variant-caps: small-caps;
  font-size: 0.5em;
  line-height: 1;
}

/* ===== 2) Topbar header (mobile-first) ===== */
.topbar{
  position: sticky; top: 0; z-index: 1000;
  display: flex; align-items: center; gap: 1rem;
  background: #A51931; color: #fff;
  padding: .5rem .75rem; border-bottom: none;
}
/* Title link: white, no hover underline */
.topbar > a:first-of-type{
  color:#fff; text-decoration:none; font-weight:600;
}
.topbar > a:first-of-type:hover,
.topbar > a:first-of-type:focus{
  text-decoration:none; /* no hover effect */
}
/* Accessible focus ring */
.topbar > a:first-of-type:focus-visible{
  outline:2px solid #fff; outline-offset:2px;
}

/* Hidden checkbox & hamburger icon */
.menu-toggle{ position:absolute; left:-9999px; }
.hamburger{ display:block; cursor:pointer; margin-left:auto; padding:.25rem; }
.hamburger span{ display:block; width:24px; height:2px; background:#fff; margin:5px 0; }

/* ===== 3) Navlinks — single source of truth ===== */
/* Mobile-first: dropdown is WHITE panel with BLACK links */
.navlinks{
  display:none;
  position:absolute; left:0; right:0; top:100%;
  background:#fff; color:#111;
  border:1px solid #e5e7eb;
  box-shadow:0 2px 6px rgba(0,0,0,.12);
  padding:.5rem;
  flex-direction:column; gap:0;
}
.navlinks a{
  color:#111; text-decoration:none;
  padding:.5rem; border-radius:.375rem;
}
.navlinks a:hover, .navlinks a:focus{
  background:#f2f2f2; color:#111;
}
/* Toggle open */
.menu-toggle:checked ~ .navlinks{ display:flex; }

/* Desktop (≥768px): right-justified, transparent on crimson, WHITE links */
@media (min-width:768px){
  .hamburger{ display:none; }
  .navlinks{
    margin-left:auto;
    position:static; background:transparent; border:0; box-shadow:none;
    display:flex; flex-direction:row; gap:.75rem; padding:0;
  }
  .navlinks a{
    background:transparent; color:#fff; padding:.25rem .5rem; border-radius:.375rem;
  }
  .navlinks a:hover, .navlinks a:focus{
    background:rgba(255,255,255,.18); color:#fff;
  }
}

/* ===== 4) Letter navbar (Bootstrap-like nav-pills) ===== */
#letter-nav{
  display:flex; flex-wrap:wrap; align-items:center;
  gap:.25rem; padding:.25rem;
  background:#f8f9fa; border:1px solid #e9ecef; border-radius:.5rem;
}
#letter-nav .nav-link{
  display:inline-block; padding:.25rem .5rem;
  font-size:1.0rem; line-height:1.0;
  color:#0d6efd; text-decoration:none;
  border:1px solid transparent; border-radius:9999px; /* pill */
  transition:background-color .15s ease, color .15s ease, border-color .15s ease, box-shadow .15s ease;
}
#letter-nav .nav-link:hover{
  background:rgba(13,110,253,.08); border-color:rgba(13,110,253,.2);
}
#letter-nav .nav-link.active{
  color:#fff; background:#0d6efd; border-color:#0d6efd;
}
#letter-nav .nav-link:focus-visible{
  outline:none; box-shadow:0 0 0 .2rem rgba(13,110,253,.25);
}
#letter-nav .nav-link.disabled{ pointer-events:none; opacity:.5; }

/* ===== 5) Dictionary entries ===== */
p{
  text-indent:-1.5em; margin-left:1.5em; margin-bottom:0.2em;
}
p.no-hang { 
  text-indent: 0; 
  margin-left: 0; 
}
dt {
font-style:italic;
font-weight:bold;
}
.short{ cursor:pointer; }
.short:hover{ background:#f8f9fa; }
.entry.expanded{
  background:#f7f7f7; border-color:#e2e3e5;
  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.04);
}

/* Full-width search row */
.searchbar{
  display:flex; align-items:stretch; gap:.5rem;
  width:100%; margin:.75rem 0;
}
.searchbar input[type="text"]{
  flex:1 1 auto; min-width:0;
  font-size:1rem; padding:.5rem .75rem;
  border:1px solid #ced4da; border-radius:.375rem;
}
.searchbar button{
  flex:0 0 auto;
  font-size:1rem; padding:.5rem .9rem;
  border:1px solid #ced4da; border-radius:.375rem;
  background:#fff; cursor:pointer;
}
.searchbar button:hover{ background:#f1f3f5; }

#search-results .long{ display:none; }               /* keep search results “short” */
#search-results mark{ background:#fff3cd; padding:0 .1em; }  /* highlight hits */

.dfn{ margin-left:.35rem; opacity:.85; font-style:italic; }

/* Minimal replacements for Bootstrap badge utilities used in markup */
.text-bg-secondary{ background:#6c757d; color:#fff; }
.ms-1{ margin-left:.25rem; }
.badge.level{
  display:inline-flex; align-items:center; justify-content:center;
  padding:.15em .45em; line-height:1.15; font-size:.85em; border-radius:9999px;
}

/* ===== 6) Static “pages” (About / Credits) ===== */
.hidden{ display:none !important; }
.page-view{
  position:relative; display:block; min-height:60vh;
  max-width:900px; margin:1rem auto; padding:1rem 1.25rem;
  background:#fff; border:1px solid #e5e7eb; border-radius:.5rem;
  box-shadow:0 1px 2px rgba(0,0,0,.04);
}
.page-view .lead{ font-size:1.1rem; opacity:.9; }
.page-view .back{
  position:absolute; top:.75rem; right:.75rem;
  font-size:.9rem; padding:.35rem .7rem;
  background:#fff; border:1px solid #ced4da; border-radius:.375rem; cursor:pointer;
}
.page-view .back:hover{ background:#f1f3f5; }

/* back buttons/links: no underline in any state */
.page-view .back,
.page-view .back:link,
.page-view .back:visited,
.page-view .back:hover,
.page-view .back:focus,
.page-view .back:active {
  text-decoration: none;
  color: inherit; /* keep current text color */
}

/* CSS-only view switching (About shown by default) */
#views > *{ display:none; }
#views > #page-about{ display:block; }

/* Show About */
#about:target ~ #views > *{ display:none; }
#about:target ~ #views > #page-about{ display:block; }

/* Show Credits */
#credits:target ~ #views > *{ display:none; }
#credits:target ~ #views > #page-credits{ display:block; }

/* Show Dictionary */
#dictionary:target ~ #views > *{ display:none; }
#dictionary:target ~ #views > #dictionary-view{ display:block; }

/* Reduce jump under sticky header when following hash */
#about, #credits, #dictionary{ scroll-margin-top: 72px; }

/* ===== 7) Mobile tweaks (iPhone readability, denser pills, smaller title) ===== */
@media (max-width:576px){
  html{ font-size: 18px; }

  /* Smaller single-line title with ellipsis */
  .topbar{ padding:.4rem .6rem; }
  .topbar > a:first-of-type{
    flex:1 1 auto; min-width:0;
    font-size:.85rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  }
  .hamburger{ padding:.2rem; }
  .hamburger span{ width:22px; }

  /* Search & entries readability */
  .searchbar input[type="text"],
  .searchbar button{ font-size: 1.1rem; }
  #letter-nav{ gap:.2rem; padding: 0.1rem; }
  #letter-nav .nav-link{ font-size: 1.0rem; padding: 0.1rem 0.1rem; }
  .short p, .long{ font-size:1.1rem; line-height:1.45; }
  .page-view{ padding: 1rem; margin:.75rem auto; }
  .page-view .back{ top:.5rem; right:.5rem; font-size:1rem; padding:.45rem .85rem; }
}
    """
    script = """
    <script>
      function toggleEntry(id) {
        const entryEl = document.getElementById(id);
        const longEl = document.getElementById(id + '-long');
        if (!longEl) return;
        const show = (longEl.style.display === 'none');
        longEl.style.display = show ? 'block' : 'none';
        if (entryEl) entryEl.classList.toggle('expanded', show);
      }

      function showLetter(letter) {
        document.querySelectorAll('.letter-section').forEach(s => s.style.display = 'none');
        const results = document.getElementById('search-results');
        if (results) results.style.display = 'none';
        const section = document.getElementById('section-' + letter);
        if (section) section.style.display = 'block';
        document.querySelectorAll('#letter-nav .nav-link').forEach(a => a.classList.remove('active'));
        const link = Array.from(document.querySelectorAll('#letter-nav .nav-link')).find(a => a.textContent.trim() === letter);
        if (link) link.classList.add('active');
        return false;
      }

      function hideAllSections() {
        document.querySelectorAll('.letter-section').forEach(s => s.style.display = 'none');
      }

      function stripIdsDeep(node) {
        if (node.nodeType === 1 && node.hasAttribute('id')) node.removeAttribute('id');
        for (const child of (node.children || [])) stripIdsDeep(child);
      }

      function resetSearch() {
        const input = document.getElementById('search-box');
        if (input) input.value = '';
        const resultsDiv = document.getElementById('search-results');
        if (resultsDiv) resultsDiv.style.display = 'none';
        document.getElementById('letter-nav').style.display = 'flex';
        hideAllSections();
        const first = document.querySelector('.letter-section');
        if (first) first.style.display = 'block';
      }

      function handleSearch(input) {
        const query = input.value.toLowerCase();
        const resultsDiv = document.getElementById('search-results');
        const navBar = document.getElementById('letter-nav');
        if (!resultsDiv) return;
        resultsDiv.innerHTML = '';

        if (query.length === 0) {
          resetSearch();
          return;
        }
        
        // Debounce helper: run fn only after the user stops typing for N ms
        function debounce(fn, ms = 200) {
          let t;
          return function (...args) {
            clearTimeout(t);
            t = setTimeout(() => fn.apply(this, args), ms);
            };
          }

        // Create a debounced version of your existing handleSearch
        // (handleSearch(input) should already be defined elsewhere)
        window.debouncedSearch = debounce(handleSearch, 200);

        navBar.style.display = 'none';
        hideAllSections();
        resultsDiv.style.display = 'block';

        document.querySelectorAll('.entry').forEach(entry => {
          const shortText = entry.querySelector('.short')?.textContent.toLowerCase() || '';
          if (shortText.includes(query)) {
            const clone = entry.cloneNode(true);
            stripIdsDeep(clone);
            const long = clone.querySelector('.long');
            if (long) long.style.display = 'none';
            resultsDiv.appendChild(clone);
            highlightInElementFold(clone.querySelector('.short'), input.value);
          }
        });

        if (resultsDiv.children.length === 0) {
          resultsDiv.innerHTML = '<p class="text-muted">No results found.</p>';
        }
      }

      document.addEventListener('DOMContentLoaded', () => {
        const first = document.querySelector('.letter-section');
        if (first) first.style.display = 'block';
        const firstLink = document.querySelector('#letter-nav .nav-link');
        if (firstLink) firstLink.classList.add('active');
      });
      function fold(s){ return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase(); }
      function highlightInElementFold(el, query){
          if (!el || !query) return;
          const qf = fold(query);
          const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
          const nodes = [];
          while (tw.nextNode()) nodes.push(tw.currentNode);

          for (const node of nodes){
            const text = node.nodeValue;
            // Build folded string + map from folded index -> original index
            let folded = '';
            const map = [];
            for (let i=0; i<text.length; i++){
              const f = fold(text[i]);
              folded += f;
              for (let k=0; k<f.length; k++) map.push(i);
            }

            let pos = 0, prevOrig = 0, changed = false;
            const frag = document.createDocumentFragment();

            while (true){
              const hit = folded.indexOf(qf, pos);
              if (hit === -1) break;
              const startOrig = map[hit];
              const endOrig = map[hit + qf.length - 1] + 1;

              if (startOrig > prevOrig) frag.appendChild(document.createTextNode(text.slice(prevOrig, startOrig)));
              const mark = document.createElement('mark');
              mark.textContent = text.slice(startOrig, endOrig);
              frag.appendChild(mark);

              prevOrig = endOrig;
              pos = hit + qf.length;
              changed = true;
            }
            if (changed){
              if (prevOrig < text.length) frag.appendChild(document.createTextNode(text.slice(prevOrig)));
              node.parentNode.replaceChild(frag, node);
            }
          }
        }
    </script>
    """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
      <title>Tamang Dictionary</title>
      <style>
        {style}
      </style>
    </head>
    <body>
<!-- Standalone header with hamburger -->

<header class="topbar">
  <a href="#dictionary">Tamang | Nepali – French – English Dictionary</a>

  <input type="checkbox" id="menu-toggle" class="menu-toggle" aria-label="Toggle navigation">
  <label for="menu-toggle" class="hamburger" aria-hidden="true">
    <span></span><span></span><span></span>
  </label>

  <nav class="navlinks">
    <a href="#about" onclick="document.getElementById('menu-toggle').checked=false">About</a>
    <a href="#credits" onclick="document.getElementById('menu-toggle').checked=false">Credits</a>
  </nav>
</header>

<!-- invisible anchors used by :target -->
<span id="about" aria-hidden="true"></span>
<span id="credits" aria-hidden="true"></span>
<span id="dictionary" aria-hidden="true"></span>

<!-- About page (hidden by default) -->
<div id="views">
  <!-- About is default (visible when no hash) -->
  <section id="page-about" class="page-view">
    <a class="back" href="#dictionary">Close</a>
    <h2>About</h2>
    <p class="lead no-hang">
    This is an early prototype of an online dictionary for the
    Tamang language of Nepal that works on both mobile devices
    and "desktop" computers. It is built as a single standalone
    HTML page: it requires a web browser but does not require a
    connection to the internet.
    </p>
    <p class="no-hang">
    Two facilities for searching the dictionary are provided:
    <ul>
    <li>Point-and-click searching using the ordered initial
    "letters" shown in the navigation bar.</li>
    <li>A "search box" that performs an instantaneous
    <i>free text</i> search of the entire dictionary.</li>
    </ul>
    </p>
    <p class="no-hang">
    The dictionary contains 3,517 entries, and most have definitions
    in three languages: Nepali (in Devanagari with transliteration),
    French, and English. 
    </p>
    <p class="no-hang">
    Continue to <a href="./dictionary.html#dictionary">The Dictionary</a>. 
    </p>

  </section>

<!-- Credits page (hidden by default) -->
  <section id="page-credits" class="page-view">
    <a class="back" href="#dictionary">Close</a>
    <h2>Acknowledgements</h2>
    <dl>
      <dt>Dictionary</dt> <dd>the machine-readable dictionary used in this application is a
      work-in-progress by Martine Mazaudon (CNRS). The dictionary is the result of
      over 50 years of fieldwork in Nepal and careful lexicography. The original
      digital version is in 
      <a href="http://www.montler.net/lexware/" target="_blank">Lexware</a> format,
      a computational dictionary tool written some 60 years ago.
      </dd>
      <dt>Software</dt> <dd>this "HTML only" version of the dictionary was created by a Python
      script written by John B. Lowe (UC Berkeley) with the help with ChatGPT. The CSS styling is
      based on Bootstrap 5, but the minimal CSS and Javascript needed to drive the application
      was extracted and is included inline. The page can be found on the web at
      <a href="https://projects.johnblowe.com/dictionary.html">https://projects.johnblowe.com/dictionary.html</a>
      </dd>
    </dl>
    <p class="no-hang">
    Please send comments, suggestions, indeed any feedback to
    <a href="mailto:example@example.com">the creators</a>. We would love to hear what you think.
    </p>
    </section>
    
  <div id="dictionary-view">
      <div class="searchbar">
        <input id="search-box" type="text" placeholder="Search entries..."
        oninput="(window.debouncedSearch || handleSearch)(this)">
        <button type="button" onclick="resetSearch()">Reset</button>
      </div>

      {nav_bar}

      {content_divs}

      <div id="search-results" class="mt-4" style="display:none;"></div>
      {script}
    </div>
  </div>
</body>
</html>
    """
    return html

# ---------- CLI ----------
if __name__ == "__main__":
    xml_path = "chunk.xml"
    out_html = "dictionary.html"

    entries = parse_entries_from_file(xml_path)
    html_output = generate_html(entries)
    html_output = minify_html(html_output)
    Path(out_html).write_text(html_output, encoding='utf-8')
    print(f"✅ Wrote {out_html}")
