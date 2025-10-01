import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path
from html import escape, unescape
import re
import unicodedata

# ============== helpers ==============

MASTER_BAND_LIST = set('cf dfbot dfe dff dfn dfzoo dial emp il mmnag nag nb niv phr ps rajdfn rajnag var xr'.split(' '))
SPECIAL_BANDS = set('hw hwdial ps dff dfe nag dfn il phr cf xr emp dfbot dfzoo'.split(' '))
ALL_BANDS = MASTER_BAND_LIST | SPECIAL_BANDS
DEFAULT_BANDS = MASTER_BAND_LIST - SPECIAL_BANDS
# lists we collect into arrays
TAGS_LIST = ['phr', 'gram', 'xr', 'so', 'rec', 'nb', 'nbi', 'il', 'ilold', 'enc', 'cf']
# dict for xrefs
KEYS = {}

def trans_str(s):
    source_chars = '012345:AEONT'
    target_chars = unescape('&#x2070;¹²³&#x2074;&#x2075;&#x02d0;&#x0259;&#x025b;&#x0254;&#x014b;&#x0288;')
    table = str.maketrans(source_chars, target_chars)
    s = s.translate(table)
    s = s.replace('ng', unescape('&#x014b;'))
    s = s.replace('aM', unescape('a&#x0303;'))
    s = s.replace('eM', unescape('e&#x0303;'))
    s = s.replace('iM', unescape('i&#x0303;'))
    s = s.replace('oM', unescape('o&#x0303;'))
    s = s.replace('uM', unescape('u&#x0303;'))
    s = s.replace('ph', unescape('p&#x02b0;'))
    s = s.replace('th', unescape('t&#x02b0;'))
    s = s.replace('ch', unescape('c&#x02b0;'))
    s = s.replace('kh', unescape('k&#x02b0;'))
    s = s.replace(unescape('&#x0288;h'), unescape('&#x0288;&#x02b0;'))
    return s


def esc(s):
    s = re.sub(r' ?<.*?>', '', s or '')
    s = re.sub(r'/(.*?)/', lambda m: render_tamang(m.group(1)), s)
    # complicated cause we only want to remove | if it is preceded by *
    s = re.sub(r'\*([^| ]+)\||\*', lambda m: m.group(1) or '', s)
    # escape seems not to be needed
    # s = escape(s, quote=True)
    # render tamang text if between //
    s = unicodedata.normalize('NFC', s)
    # Replace COMBINING CANDRABINDU (U+0310) with COMBINING DOT ABOVE (U+0307)
    return s.replace("\u0310", "\u0307")


def render_special(s):
    # following hack is needed to avoid 'eau de cuisson de la boule de farine (<i>ḍhim</i>̇ḍo)'
    s = re.sub(r'\$([^\s]+)', r'<i>\1</i>', s)  # $token + word boundary -> italic
    s = re.sub(r'\%(.+?)\|', r'<i>\1</i>', s)  # %free text| -> italic
    return s

def render_tamang(t):
    t = re.sub(r' ?<.*?>', '', t or '').strip()
    # protect nepali forms in tamang transcription
    tokens = re.split(r'(\$.+?)\b', t)
    converted_tokens = []
    for tok in tokens:
        if '$' in tok:
            converted_tokens.append(re.sub(r'\$(.+?)\b', r'<i>\1</i>', tok))
        else:
            converted_tokens.append(trans_str(tok))
    return f"<b>{''.join(converted_tokens)}</b>"


def render_transliteration(t):
    return f'<i>{esc(t)}</i>' if t else ''


def render_cf(t):
    if t:
        # the initial blank is important
        link = f'''onclick="return toggleEntryAll('{KEYS.get(t[0], 'nokey')}')"'''
        return f' &#x2192; <a href="#" {link}>{render_tamang(t[0])}</a>'
    else:
        return ''


def render_var(t):
    if t:
        t = re.sub(r' ?<.*?>', '', t or '').strip()
        t = render_2part(t)
        return f' &#160; [<span class="small-caps">var</span> {t.strip()}]'
    else:
        return ''


def render_dfbot(t):
    if t:
        t = re.sub(r' ?<.*?>', '', t or '').strip()
        parts = t.split(',')
        if len(parts) == 1:
            t = f'<i>{esc(parts[0])}</i>' if t else ''
        else:
            t = f'<i>{esc(parts[0])}</i>,' + ' '.join(parts[1:])
        return f'<span class="small-caps">[bot] </span> {t.strip()}'
    else:
        return ''


def render_emp(t):
    if t:
        result = render_special(esc(t))
        if '?nep' in t or 'nep' in t:
            if 'nep ' not in result:
                return f' &#160; &lt;{result}'
            v1 = [m for m in re.match(r'(\?? ?nep) +(.*)', result).groups()]
            if len(v1) == 2:
                # v1[1] = render_special(v1[1])
                v2 = v1[1].split("'")
                if len(v2) > 1:
                    v3 = render_transliteration(v2[0])
                    result = f"{v1[0]} {v3} '{v2[1]}'"
                else:
                    result = f"{v1[0]} {render_transliteration(v2[0])}"
            else:
                result = f'{v1[0]} {render_transliteration(v1[1])}'
        # the initial blank is important
        return f' &#160; &lt;{result}'
    else:
        return ''


def render_sense_number(t):
    return f' <small>[{esc(t)}]</small>'


def render_2part(part):
    part = render_special(part)
    try:
        parts = part.split('|')
        tamang = parts[0]
        tamang = render_tamang(tamang)
        # U+0307  BULLET (we'll visually separate parts)
        bullet = ' &bull; '
        trans = f"{render_special(bullet.join(parts[1:]))}"
        trans = f' &#160; {trans}' if trans else ''
        return (f'{tamang}{trans}')
    except Exception:
        # if the split does not work, render the whole thing as Tamang
        if '|' in part:
            print(f'split failed: {part}')
        return (render_tamang(part))

# =================== parsing ===================

def localname(tag: str) -> str:
    """Strip XML namespace and lowercase."""
    if not tag:
        return ''
    return tag.split('}', 1)[-1].lower()


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
    level = mode_el.attrib.get('level') or mode_el.attrib.get('n') or str(idx)
    m = {
        'id': f'{base_id}-m{idx}',
        'level': level,
        'dff': get_text(mode_el, 'dff'),
        'dfe': get_text(mode_el, 'dfe'),
        'nag': get_text(mode_el, 'nag'),
        'dfn': get_text(mode_el, 'dfn'),
        'dfzoo': get_text(mode_el, 'dfzoo'),
        'dfbot': get_text(mode_el, 'dfbot'),
        'ps': get_text(mode_el, 'ps'),
        'hw': get_text(mode_el, 'hw'),
        'sem': get_text(mode_el, 'sem'),
        'var': get_text(mode_el, 'var'),
        # arrays
        'phr': [], 'gram': [], 'xr': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [],
        'il': [], 'ilold': [], 'enc': [], 'cf': [],
    }
    m.update(collect_texts(mode_el, TAGS_LIST))
    return m


def parse_sub(sub_el, base_id, idx):
    s = {
        'id': f'{base_id}-s{idx}',
        'hw': get_text(sub_el, 'hw'),
        'ps': get_text(sub_el, 'ps'),
        'dff': get_text(sub_el, 'dff'),
        'dfzoo': get_text(sub_el, 'dfzoo'),
        'dfbot': get_text(sub_el, 'dfbot'),
        'dfe': get_text(sub_el, 'dfe'),
        'nag': get_text(sub_el, 'nag'),
        'dfn': get_text(sub_el, 'dfn'),
        'sem': get_text(sub_el, 'sem'),
        'var': get_text(sub_el, 'var'),
        # arrays
        'phr': [], 'gram': [], 'xr': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [],
        'il': [], 'ilold': [], 'enc': [], 'cf': [],
        'modes': []
    }
    s.update(collect_texts(sub_el, TAGS_LIST))
    for midx, mode_el in enumerate(sub_el.findall('mode'), 1):
        s['modes'].append(parse_mode(mode_el, s['id'], midx))
    return s


def parse_entry(entry_el, i):
    e = {
        'id': entry_el.attrib.get('id', f'e{i}'),
        'hw': get_text(entry_el, 'hw'),
        'ps': get_text(entry_el, 'ps'),
        'dff': get_text(entry_el, 'dff'),
        'dfe': get_text(entry_el, 'dfe'),
        'dfbot': get_text(entry_el, 'dfbot'),
        'dfzoo': get_text(entry_el, 'dfzoo'),
        'nag': get_text(entry_el, 'nag'),
        'dfn': get_text(entry_el, 'dfn'),
        'sem': get_text(entry_el, 'sem'),
        'var': get_text(entry_el, 'var'),
        'emp': get_text(entry_el, 'emp'),
        'ton': get_text(entry_el, 'ton'),
        # arrays
        'phr': [], 'gram': [], 'xr': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [],
        'il': [], 'ilold': [], 'enc': [], 'cf': [],
        'modes': [],
        'subs': [],
    }
    e.update(collect_texts(entry_el, TAGS_LIST))

    for idx, mode_el in enumerate(entry_el.findall('mode'), 1):
        e['modes'].append(parse_mode(mode_el, e['id'], idx))
    for sidx, sub_el in enumerate(entry_el.findall('sub'), 1):
        e['subs'].append(parse_sub(sub_el, e['id'], sidx))

    return e


def slugify(label: str, used: set) -> str:
    base = re.sub(r'\s+', '-', (label or '').strip().lower())
    base = re.sub(r'[^a-z0-9\-]+', '', base)
    if not base:
        base = 'g'
    token = base
    n = 2
    while token in used:
        token = f"{base}-{n}"
        n += 1
    used.add(token)
    return token


def parse_entries_from_file(xml_path):
    """Group entries by in-stream <hdr> separators, preserving order. Accept any root wrapper."""
    raw = Path(xml_path).read_text(encoding='utf-8')
    root = ET.fromstring(raw)

    groups = OrderedDict()
    used = set()
    current_token = None
    i = 0

    for node in root.iter():
        tag = localname(getattr(node, 'tag', ''))
        if tag == 'hdr':
            label = (node.text or '').strip()
            token = slugify(label or 'g', used)
            label = trans_str(label)
            groups.setdefault(token, {'label': label, 'entries': []})
            current_token = token
        elif tag == 'entry':
            e = parse_entry(node, i)
            KEYS[e.get('hw', 'nokey')] = e['id']
            i += 1
            if not e.get('hw'):
                # print(f"no hw, skipped: {e.get('id')}")
                continue
            if current_token is None:
                token = slugify('0', used)
                groups.setdefault(token, {'label': '0', 'entries': []})
                current_token = token
                print(f"current_token is none, 0 used instead: {current_token}")
            groups[current_token]['entries'].append(e)

    return groups

# =================== rendering ===================

def render_lang_lines(ps, nag, dfn, dff, dfe):
    """Return HTML lines for np/fr/en without emitting empties. np line shows nag (if any) with optional dfn."""
    lines = []
    if ps:
        lines.append(f'<span class="small-caps"><span class="xxx">{esc(ps)}</span></span>')
    if nag or dfn:
        np_line = f'<span class="small-caps">nep</span>'
        if nag:
            np_line += f' {esc(nag)} &#160;'
        if dfn:
            np_line += f' <span class="dfn">{render_transliteration(dfn)}</span>'
        lines.append(np_line)
    if dff:
        lines.append(f'<span class="small-caps">fr&#160;</span> <span class="xxx">{render_special(esc(dff))}</span>')
    if dfe:
        lines.append(f'<span class="small-caps">eng</span> <span class="xxx">{render_special(esc(dfe))}</span>')
    if not lines:
        return ""
    return "<br/>".join(lines)

def render_long_bits(d):
    parts = []
    # if d.get('sem'):
    #     parts.append(f"<div class='mb-1'><b>Semantic domain:</b> {esc(d['sem'])}</div>")
    # [dial]
    ils = d.get('il', [])
    if ils:
        items = ''.join(f'<p>{render_2part(il)}</p>' for il in ils)
        # parts.append(f'<span>{items}</span>')
        parts.append(items)
    for phr in d.get('phr', []):
        parts.append(f'<div class="mb-1"><i>phr </i> {render_2part(phr)}</div>')
    # for gram in d.get('gram', []):
    #    parts.append(f"<div class='mb-1'><b>grammar:</b> <i>{esc(gram)}</i></div>")
    # for enc in d.get('enc', []):
    #    parts.append(f"<div class='mb-1'><b>note (enc):</b> {esc(enc)}</div>")
    # for nb in d.get('nb', []):
    #     parts.append(f"<div class='mb-1'><i>note </i> {esc(nb)}</div>")
    # for nbi in d.get('nbi', []):
    #     parts.append(f"<div class='mb-1'><i>note (internal):</i> {esc(nbi)}</div>")
    dfbot = d.get('dfbot', '')
    parts.append(f"<div class='mb-1'>{render_dfbot(dfbot)}</div>")
    for xr in d.get('xr', []):
        parts.append(f"<div class='mb-1'><i>cf </i> {render_tamang(xr)}</div>")
    # for so in d.get('so', []):
    #     parts.append(f"<div class='mb-1'><b>Source:</b> {esc(so)}</div>")
    # for rec in d.get('rec', []):
    #    parts.append(f"<div class='mb-1'><b>Recorded:</b> {esc(rec)}</div>")
    return ''.join(parts)

def render_mode_block(m):
    mid = m['id']
    has_level = bool(m.get('level'))
    badge_html = f"<span class='badge text-bg-secondary level'>{str(m['level'])}</span>" if has_level else ''
    if badge_html:
        badge_html = f'<div class="mode-badge">{badge_html}</div>'
    lines = render_lang_lines('', m.get('nag', ''), m.get('dfn', ''), m.get('dff', ''), m.get('dfe', ''))
    short_html = ""
    if lines:
        short_html = f"""
        <div class="mode-short">
          {badge_html}
          <div class="mode-sub"><p class="mb-0">{lines}</p></div>
        </div>"""
    long_bits = render_long_bits(m)
    head_bits = ""
    # if m.get('hw') or m.get('ps'):
    #     ps_html = f'& <i class="small-caps">{esc(m.get("ps",""))}</i>' if m.get('ps') else ''
    #     head_bits = f"<div class='mode-head mb-1'><b>{esc(m.get('hw',''))}</b>{ps_html}</div>"
    long_html = f"""
      <div class="mode-long" id="{mid}-long" style="display:none;">
        <div class="mode-body">{head_bits}{long_bits}</div>
      </div>"""
    return f"<div class='mode-sub'>{short_html}{long_html}</div>"

def render_sub_block(s):
    sid = s['id']
    head_html = render_hw_etc(s)
    lines = render_lang_lines('', s.get('nag',''), s.get('dfn',''), s.get('dff',''), s.get('dfe',''))
    short_lines = (head_html + (f"<p class='mb-0'>{lines}</p>" if lines else "")) if (head_html or lines) else ""
    short_html = ""
    if short_lines:
        short_html = f"""
          <div class="mode-body">{short_lines}</div>
        """
    long_bits = render_long_bits(s)
    long_html = f"""
      <div class="mode-long" id="{sid}-long" style="display:none;">
        <div class="mode-body">{long_bits}</div>
      </div>"""
    mode_blocks = ''.join(render_mode_block(m) for m in s.get('modes', []))
    return f"<div class='mode-block'>{short_html}{long_html}{mode_blocks}</div>"

def render_hw_etc(entry):
    hw = entry.get('hw', None)
    if 'lahara' in hw:
        pass
    homonym = re.match(r'([^\s]+)\$(.*)', hw)
    ps_html = f'&#160;<i class="small-caps">{esc(entry["ps"])}</i>' if entry.get('ps') else ''
    cf_html = render_cf(entry.get('cf', None))
    emp_html = render_emp(entry.get('emp', None))
    var_html = render_var(entry.get('var', None))
    if homonym:
        hw = homonym[1]
        sense_number = render_sense_number(homonym[2])
    else:
        sense_number = ''
    hw_rendered = render_tamang(hw)
    head = f'<p class="mb-0 entry-head">{hw_rendered}{sense_number}{ps_html}{cf_html}{emp_html}{var_html}</p>'
    return head if hw else ''

def render_short(entry):
    head = render_hw_etc(entry)
    blocks = []
    if entry.get('modes') or entry.get('subs'):
        if entry.get('dff') or entry.get('dfe') or entry.get('nag') or entry.get('dfn'):
            pseudo = {
                'id': f"{entry['id']}-m0",
                'level': None,
                'nag': entry.get('nag',''), 'dfn': entry.get('dfn',''),
                'dff': entry.get('dff',''), 'dfe': entry.get('dfe',''),
                'sem': entry.get('sem',''),
                'var': entry.get('var',''),
                'phr': entry.get('phr',[]), 'gram': entry.get('gram',[]), 'xr': entry.get('xr',[]),
                'so': entry.get('so',[]), 'rec': entry.get('rec',[]), 'nb': entry.get('nb',[]), 'nbi': entry.get('nbi',[]),
                'il': entry.get('il',[]), 'ilold': entry.get('ilold',[]), 'enc': entry.get('enc',[]), 'cf': entry.get('cf',[]),
            }
            blocks.append(render_mode_block(pseudo))
        for m in entry.get('modes', []):
            blocks.append(render_mode_block(m))
        for s in entry.get('subs', []):
            blocks.append(render_sub_block(s))
        body = ''.join(blocks)
    else:
        lines = render_lang_lines('', entry.get('nag',''), entry.get('dfn',''), entry.get('dff',''), entry.get('dfe',''))
        body = f"<p class='mb-0'>{lines}</p>" if lines else ""
    return f"<div class='short'>{head}{body}</div>"

def render_entry_long(entry):
    has_base_defs = entry.get('dff') or entry.get('dfe') or entry.get('nag') or entry.get('dfn')
    if (entry.get('modes') or entry.get('subs')) and has_base_defs:
        d_extras_html = ''
    else:
        d_extras_html = render_long_bits(entry)
    return d_extras_html


STYLE = r"""
:root { --font-sans: system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
html, body { height: 100%; }
body { font-family: var(--font-sans); margin: 0; display: grid; grid-template-rows: auto 1fr; height: 100vh; overflow: hidden; }
.fixed-topbar { position: relative; z-index: 1000; background: #fff; box-shadow: 0 1px 0 rgba(0,0,0,.06); overflow-x: hidden; width: 100%; }
#views { padding-top: 4px ; min-height: 0; overflow: auto; -webkit-overflow-scrolling: touch; }
#views > * { display: none !important; }
.small-caps { font-variant-caps: small-caps; font-size: .7rem; }
.mb-0 { margin-bottom: 0; }
.mb-1 { margin-bottom: 4px; }
.my-2 { margin: 6px 0 6px 0; }
.ms-1 { margin-left: .25rem; }
.header { position: sticky; z-index: 2; display: flex; align-items: center; gap: .75rem; background: #A51931; color: #fff; width: 100%; padding: .5rem; box-sizing: border-box; }
.header .logo { width: 28px; height: 28px; border-radius: 4px; background: rgba(255,255,255,.3); flex: 0 0 28px; }
.header .brand { color: #fff; text-decoration: none; font-weight: bold; overflow: hidden; }
.header .page-links { margin-left: auto; display: flex; gap: .5rem; }
.header .page-links a { color: #fff; text-decoration: none; padding: .25rem .5rem; border-radius: .375rem; }
.header .page-links a:hover { background: rgba(255,255,255,.18); }
/* Hamburger (CSS-only) */
.menu-toggle { position: absolute; left: -9999px; }
.hamburger { display: none; cursor: pointer; margin-left: auto; padding: .25rem; }
.hamburger span { display: block; width: 24px; height: 2px; background: #fff; margin: 5px 0; border-radius: 1px; }
/* Mobile: dropdown menu, etc. */
@media (max-width: 768px) {
 .hamburger { display: block; flex: 0 0 auto; margin-left: .5rem; }
 .header .brand { flex: 1 1 auto; min-width: 0; font-size:.70rem;}
 .header .page-links { display: none; position: absolute; top: 100%; left: 0; right: 0; z-index: 1200; background: #fff; border: 1px solid #e5e7eb; padding: .5rem; }
 .header .page-links a { display: block; color: #111; text-decoration: none; padding: .5rem .75rem; border-radius: .375rem; }
 .header .page-links a:hover { background: #f2f2f2; }
 #menu-toggle:checked ~ .page-links { display: block; } }
/* Search + Letter Nav */
.searchnav { display: none; background: #fff; }
.searchbar { display: flex; gap: .5rem; align-items: center; padding: .4rem .75rem; }
.searchbar input[type="text"] { flex: 1 1 auto; min-width: 0; font-size: 1rem; padding: .5rem .75rem; border: 1px solid #ced4da; border-radius: .375rem; }
.searchbar button { flex: 0 0 auto; font-size: 1rem; padding: .5rem .9rem; border: 1px solid #ced4da; border-radius: .375rem; background: #fff; cursor: pointer; }
.searchbar button:hover { background: #f1f3f5; }
#letter-nav { display: block; overflow-x: auto; overflow-y: hidden; padding: .2rem .5rem; margin: 0; border-top: 1px solid #f1f3f5; justify-content: center; }
#letter-nav .nav-link { display: inline-block; font-size: 1.2rem; line-height: 1.1; padding: .2rem; margin-right: .15rem; color: #0d6efd; text-decoration: none; border: 1px solid transparent; border-radius: 9999px; }
#letter-nav .nav-link:hover { background: rgba(13,110,253,.08); border-color: rgba(13,110,253,.2); }
#letter-nav .nav-link.active { color: #fff; background: #0d6efd; border-color: #0d6efd; }
body.show-dico .searchnav { display: block !important; }
body.show-about #page-about { display: block !important; }
body.show-credits #page-credits { display: block !important; }
body.show-dico #dictionary { display: block !important; }
#page-about { display: block; }
.page { position: relative; margin: 0 auto 1rem; padding: 0 0.4rem; background: #fff; border: 1px solid #e5e7eb; border-radius: .5rem; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
.page .to-dico { position: absolute; top: .75rem; right: .75rem; font-size: .9rem; padding: .35rem .7rem; background: #fff; border: 1px solid #ced4da; border-radius: .375rem; text-decoration: none; color: inherit; }
.page .to-dico:hover { background: #f1f3f5; }
dt { font-weight: bold; font-style: italic; }
/* Entries */
.entry { border: 1px solid #e5e7eb; border-radius: .5rem; padding: .75rem; margin: .5rem 0; background: #fff; padding-top: 0; }
.entry.expanded { background: #f7f7f7; }
.short { cursor: pointer; margin-bottom: 6px; }
.short:hover { background: #f8f9fa; }
.entry .short .entry-head { margin: 4px 0; }
/* place a subtle indicator on entries that have sub/mode blocks */
.entry { position: relative; }
.entry.has-more::after { content: '▸'; position: absolute; top: .4rem; right: .5rem; font-size: 1.6rem; color: #343a40; opacity: .95; line-height: 1; pointer-events: none; }
.entry.expanded.has-more::after { content: '▾'; font-size: 1.6rem; color: #212529; opacity: .95; }
/* Modes / Subentries */
.mode-block { margin: .35rem 0 .5rem 1rem; }
.mode-short, .mode-long { display: grid; grid-template-columns: auto minmax(0,1fr); column-gap: .5rem; align-items: start; }
.mode-long, .long p { margin: 4px 0 4px 0; }
.mode-badge { width: 2.1em; display: flex; justify-content: center; align-items: flex-start; }
.mode-badge .badge { display: inline-flex; align-items: center; justify-content: center; min-width: 1.0em; padding: .15em .45em; line-height: 1.15; font-size: .85em; border-radius: 9999px; }
.mode-body { min-width: 0; }
/* .mode-body > p { margin: 0} */
.mode-short { padding: .25rem 0; border-top: 1px dashed #eee; }
.mode-short:first-child { border-top: none; }
.badge.text-bg-secondary { background: #6c757d; color: #fff; }
/* Search results */
#search-results mark { background: #fff3cd; padding: 0 .1em; }
#search-results .long, #search-results .mode-long { display: none; }
/* Wrapping / Gloss layout */
/* .mode-body p, .mode-sub p, .entry-head, mark { overflow-wrap: break-word; word-break: normal; } */
.mode-body p, .mode-sub p { margin: .15rem 0 0; text-indent: 0; }
.mode-body p .small-caps, .mode-sub p .small-caps { display: inline-block; text-align: left; }
.mode-body p .dfn, .mode-sub p .dfn { margin-left: .35em; }
/* Responsive tweaks */
@media (max-width: 600px) {
  .mode-sub p .small-caps, .mode-body p .small-caps { min-width: 2.2em; }
 }
@media (max-width: 576px) {
  html { font-size: 18px; }
  .header .brand { font-size: .7rem; }
  #letter-nav .nav-link { font-size: 1.0rem; padding: .2rem; }
  .short p, .long { font-size: .9rem; line-height: 1.2; }
 }
"""

SCRIPT = r"""
//<![CDATA[
// ----- Entry-wide toggle: show/hide ALL long blocks within the entry -----
function toggleEntryAll(id){
  const entry = document.getElementById(id);
  if (!entry) return false;
  const longs = entry.querySelectorAll('.long, .mode-long');
  let anyHidden = false;
  longs.forEach(el => { if (el.style.display === 'none' || el.style.display === '') anyHidden = true; });
  longs.forEach(el => { el.style.display = anyHidden ? 'block' : 'none'; });
  entry.classList.toggle('expanded', anyHidden);
  return false;
}
// Legacy wrapper in case something still calls toggleEntry
function toggleEntry(id){ return toggleEntryAll(id); }

// ----- Letter navigation -----
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

// ----- Search (debounced) + highlight -----
function debounce(fn, ms=100){ let t; return (...args)=>{ clearTimeout(t); t=setTimeout(()=>fn(...args), ms); }; }
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
      if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last))); // fixed
      node.parentNode.replaceChild(frag, node);
    }
  }
}
function hideAllSections(){ document.querySelectorAll('.letter-section').forEach(s => s.style.display = 'none'); }
function resetSearch(){
  const input = document.getElementById('search-box'); if (input) input.value = '';
  const resultsDiv = document.getElementById('search-results'); if (resultsDiv) resultsDiv.style.display = 'none';
  const navBar = document.getElementById('letter-nav'); if (navBar) navBar.style.display = '';
  hideAllSections();
  const first = document.querySelector('.letter-section'); if (first) first.style.display = 'block';
  document.querySelectorAll('#letter-nav .nav-link').forEach(a => a.classList.remove('active'));
  const firstLink = document.querySelector('#letter-nav .nav-link'); if (firstLink) firstLink.classList.add('active');
  return false;
}
function handleSearch(input){
  const q = (input && input.value ? input.value : '').trim();
  const resultsDiv = document.getElementById('search-results'); if (!resultsDiv) return;
  const navBar = document.getElementById('letter-nav');
  resultsDiv.innerHTML = '';
  if (q.length === 0){ resetSearch(); return; }
  if (navBar) navBar.style.display = 'none';
  hideAllSections();
  resultsDiv.style.display = 'block';
  document.querySelectorAll('.entry').forEach(entry => {
    const shortArea = entry.querySelector('.short');
    const shortText = shortArea ? (shortArea.textContent || '') : '';
    if (shortText.toLowerCase().includes(q.toLowerCase())){
      const clone = entry.cloneNode(true);
      clone.querySelectorAll('[id]').forEach(n => n.removeAttribute('id'));
      clone.querySelectorAll('.long, .mode-long').forEach(n => n.style.display = 'none');
      resultsDiv.appendChild(clone);
      const shortClone = clone.querySelector('.short');
      if (shortClone) highlightInElement(shortClone, q);
    }
  });
  if (resultsDiv.children.length === 0){
    resultsDiv.innerHTML = '<p class="small">No results found.</p>';
  }
}
window.debouncedSearch = debounce(handleSearch, 220);


// ----- Page mode (About / Credits / Dictionary) + hamburger auto-close -----
(function () {
  function setPageFromHash(){
    const h = (location.hash || '#about').toLowerCase();
    const b = document.body.classList;
    b.remove('show-about','show-credits','show-dico');
    if (h === '#credits')      b.add('show-credits');
    else if (h === '#dico')    b.add('show-dico');
    else                       b.add('show-about');
  }

  document.addEventListener('click', function (e) {
    const a = e.target.closest('.page-links a');
    if (!a) return;
    const id = (a.getAttribute('href') || '').toLowerCase();
    if (!id.startsWith('#')) return;
    e.preventDefault();
    const cur = (location.hash || '#about').toLowerCase();
    location.hash = (cur === id) ? '#dico' : id;
    const t = document.getElementById('menu-toggle');
    if (t) t.checked = false;
  });

  window.addEventListener('hashchange', setPageFromHash);
  window.addEventListener('DOMContentLoaded', setPageFromHash);
  setPageFromHash();
})();
//]]>
"""

HTML_SHELL = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>{title}</title>
<style type="text/css">{style}</style>
</head>
<body>

<div class="fixed-topbar">
  <header class="header">
    <div class="logo" aria-hidden="true"></div>
    <a class="brand" href="#dico">{title}</a>

    <input type="checkbox" id="menu-toggle" class="menu-toggle" aria-label="Toggle navigation" />
    <label for="menu-toggle" class="hamburger" aria-hidden="true">
      <span></span><span></span><span></span>
    </label>

    <nav class="page-links">
      <a href="#about">About</a>
      <a href="#credits">Credits</a>
    </nav>
  </header>

  <div class="searchnav">
    <div class="searchbar">
      <input id="search-box" type="text" placeholder="Search entries..." oninput="debouncedSearch(this)" />
      <button type="button" onclick="resetSearch()">Reset</button>
    </div>
    {letter_nav}
  </div>
</div>

<main id="views">
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
            <dd>The machine-readable dictionary used
                in this application is a work-in-progress by Martine Mazaudon (CNRS). The dictionary is the result of
                over 50 years of fieldwork in Nepal and careful lexicography. The original
                digital version is in
                <a href="http://www.montler.net/lexware/" target="_blank">Lexware</a> format,
                a computational dictionary tool written some 50 years ago.
            </dd>
            <dt>Software</dt>
            <dd>This "HTML only" version of the dictionary was created by a Python
                script written by John B. Lowe (UC Berkeley) with the help with ChatGPT. The CSS styling is
                based on Bootstrap 5, but the minimal CSS and Javascript needed to drive the application
                was extracted and is included inline. 
            </dd>
        </dl>
        <p class="small">
            Please send comments, suggestions, indeed any feedback to
            <a href="mailto:johnblowe@gmail.com,mazaudon@gmail.com">the creators</a>. We would love to hear what you think.
        </p>
    </section>

  <section id="dictionary" class="page">
    <div class="dictionary-body">
      <div id="search-results" style="display:none;"></div>
      <div id="sections-wrapper">{sections}</div>
    </div>
  </section>
</main>

<script type="text/javascript">{script}</script>
</body>
</html>
"""

def build_letter_nav(groups):
    links = []
    first = True
    for tok, meta in groups.items():
        label = meta['label'] if meta['label'] is not None else tok
        active = ' active' if first else ''
        links.append(f'<a class="nav-link{active}" data-token="{tok}" href="#" onclick="return showToken(\'{tok}\')">{label}</a>')
        first = False
    return '<nav id="letter-nav">' + ''.join(links) + '</nav>'

def build_sections(groups):
    out = []
    first = True
    for tok, meta in groups.items():
        entries = meta['entries']
        disp = '' if first else ' style="display:none;"'
        entry_html = []
        for e in entries:
            eid = e['id']
            short_html = render_short(e)
            long_html = render_entry_long(e)
            long_block = (
                f"<div class='long' id='{eid}-long' style='display:none;'>{long_html}</div>"
                if long_html else
                f"<div class='long' id='{eid}-long' style='display:none;'></div>"
            )
            has_more = bool(e.get('modes') or e.get('subs') or long_html)
            cls = "entry has-more" if has_more else "entry"
            entry_html.append(
                f"<div id='{eid}' class='{cls}' onclick=\"return toggleEntryAll('{eid}')\">{short_html}{long_block}</div>"
            )
        out.append(f"<div class='letter-section' id='section-{tok}'{disp}>" + ''.join(entry_html) + "</div>")
        first = False
    return ''.join(out)

def minify_html(s: str) -> str:
    s = re.sub(r'<!--.*?-->', '', s, flags=re.DOTALL)
    s = re.sub(r'> +<', '> <', s)
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
    ap = argparse.ArgumentParser(description="Render dictionary XML to standalone HTML (modes + subs), grouped by <hdr>.")
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
