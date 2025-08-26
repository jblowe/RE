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
    <html lang=\"en\">
    <head>
      <meta charset=\"UTF-8\">
      <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
      <title>Tamang Dictionary</title>
      <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
      <style>
        .small-caps {{
            font-variant: small-caps;
            font-size: 0.5em;
            line-height: 1;
            }}
        p {{
            text-indent: -1.5em;
            margin-left: 1.5em;
            margin-bottom: 0.2em;
            }}
        .short {{ cursor: pointer; }}
        .short:hover {{ background-color: #f8f9fa; }}
        nav#letter-nav {{ flex-wrap: wrap; }}
        #letter-nav {{
          padding: 0.2rem;        /* shrink the nav container padding */
          gap: 0.2rem;            /* tighten space between pills */
        }}
        #letter-nav .nav-link {{
          padding: 0.15rem 0.4rem;  /* smaller pill padding */
          margin: 0;                /* no extra margin */
          font-size: 0.85rem;        /* slightly smaller text */
          line-height: 1.1;          /* tighter vertical spacing */
        }}
        #search-results .long {{ display: none; }}
        /* Shading for expanded entries (covers short + long) */
        .entry.expanded {{
          background-color: #f7f7f7;
          border-color: #e2e3e5;
          box-shadow: inset 0 0 0 1px rgba(0,0,0,0.04);
        }}
        .dictionary-banner {{
          background-color: #A51931;
          color: white;
          text-align: center;
          padding: 0.2rem;
        }}
        /* If something upstream clips inline content, force visibility */
        .entry .short {{ overflow: visible; }}
        .badge {{ 
            display: inline;
            font-size: 0.95em;
            padding: .2em .5em;
        }}
        
        /* Mobile tweaks */
        @media (max-width: 576px) {{
          html {{ font-size: \18px; }}
          body {{ -webkit-text-size-adjust: 115%; text-size-adjust: 115%; }}
        
          /* Optional: make nav pills & entry text a bit larger too */
          #letter-nav .nav-link {{ font-size: 1.1rem; padding: 0.2rem 0.2rem; }}
          .badge {{ font-size: 0.95rem; padding: .25em .55em; }}
          .short p, .long {{ font-size: 1.1rem; line-height: 1.45; }}
        }}
        .dfn {{
          margin-left: .35rem;
          opacity: .8;            /* subtle */
          font-style: italic;     /* often transliteration */
        }}
        #search-results mark {{ background: #fff3cd; padding: 0 .1em; }}
      </style>
    </head>
    <body>
      <div class="dictionary-banner">
        <h6 class="m-0">Tamang | Nepali – French – English Dictionary</h6>
      </div>
      <div class="container my-2">
      <div class=\"input-group mb-3\">
        <input type=\"text\" id=\"search-box\" class=\"form-control\" placeholder=\"Search entries...\" oninput=\"handleSearch(this)\">
        <button class=\"btn btn-outline-secondary\" type=\"button\" onclick=\"resetSearch()\">Reset</button>
      </div>

      {nav_bar}

      {content_divs}

      <div id=\"search-results\" class=\"mt-4\" style=\"display:none;\"></div>

      {script}
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
