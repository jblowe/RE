import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path
from html import escape, unescape
import re
import unicodedata
import time

# ============== helpers ==============

MASTER_BAND_LIST = set('cf dfbot dfe dff dfn dfzoo dial emp il mmnag nag nb niv phr ps rajdfn rajnag var xr'.split(' '))
SPECIAL_BANDS = set('hw ps dff dfe nag dfn il phr cf xr emp dfbot dfzoo'.split(' '))
ALL_BANDS = MASTER_BAND_LIST | SPECIAL_BANDS
DEFAULT_BANDS = MASTER_BAND_LIST - SPECIAL_BANDS
# lists we collect into arrays
TAGS_LIST = ['phr', 'gram', 'dfbot', 'xr', 'var', 'so', 'rec', 'nb', 'nbi', 'il', 'ilold', 'enc', 'cf']
# dict for xrefs
KEYS = {}

# ── nav-bar bigram helpers ─────────────────────────────────────────────────
_NAV_DIGRAPHS = sorted(['kʰ', 'cʰ', 'ʈʰ', 'tʰ', 'pʰ'], key=lambda s: -len(s))
_NAV_VOWELS   = set('aeiouāīūãẽĩõũ')
_NAV_TONE_RE  = re.compile(r'^[0-4,]+')

def _nav_first_letter(r):
    for d in _NAV_DIGRAPHS:
        if r.startswith(d): return d
    return r[0] if r else ''

def _nav_bigram(raw_hw):
    """Two-letter nav key for a raw headword, or None to skip."""
    raw = (raw_hw or '').strip()
    if not raw or raw[0] in '$-?,': return None
    r = trans_str(_NAV_TONE_RE.sub('', raw))
    if not r: return None
    fl = _nav_first_letter(r)
    if fl in _NAV_VOWELS: return None
    rest = r[len(fl):]
    return fl + (rest[0] if rest else '')

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
    # s = re.sub(r' ?<.*?>', '', s or '')
    # complicated 'cause we only want to remove | if it is preceded by *
    s = re.sub(r'\*([^| ]+)\||\*', lambda m: m.group(1) or '', s)
    # escape seems not to be needed
    # s = escape(s, quote=True)
    s = unicodedata.normalize('NFC', s)
    # Replace COMBINING CANDRABINDU (U+0310) with COMBINING DOT ABOVE (U+0307)
    #return s.replace("\u0310", "\u0307")
    return s


def render_special(s):
    # render tamang text if between //
    s = re.sub(r'/(.*?)/', lambda m: render_tamang(m.group(1)), s)
    # following hack is needed to avoid 'eau de cuisson de la boule de farine (<i>ḍhim</i>̇ḍo)'
    s = re.sub(r'\$([^\s\|]+)', r'<i>\1</i>', s)  # $token + word boundary -> italic
    s = re.sub(r'\%(.+?)\|', r'<i>\1</i>', s)  # %free text| -> italic
    return s

def render_tamang(t):
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
        t = render_tamang(t)
        return f' &#160; [<span class="small-caps">var</span> {t.strip()}]'
    else:
        return ''


def render_dfbot(t):
    if t:
        parts = t.split(',')
        if len(parts) == 1:
            t = f'<i>{esc(parts[0])}</i>' if t else ''
        else:
            t = f'<i>{esc(parts[0])}</i>,' + ' '.join(parts[1:])
        return t.strip()
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
        bullet = ' &#x2022; '
        trans = f"{bullet.join(parts[1:])}"
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
    return re.sub(r' ?<.*?>', '', (parent.findtext(tag, '') or '').strip().replace('&', '&amp;'))


def collect_texts(parent, tags_list):
    out = {}
    for tag in tags_list:
        out[tag] = [re.sub(r' ?<.*?>', '', (el.text or '').strip().replace('&', '&amp;'))
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
        'ps': get_text(mode_el, 'ps'),
        'hw': get_text(mode_el, 'hw'),
        'sem': get_text(mode_el, 'sem'),
        # arrays
        'phr': [], 'gram': [], 'xr': [], 'dfbot': [], 'var': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [],
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
        'dfe': get_text(sub_el, 'dfe'),
        'nag': get_text(sub_el, 'nag'),
        'dfn': get_text(sub_el, 'dfn'),
        'sem': get_text(sub_el, 'sem'),
        # arrays
        'phr': [], 'gram': [], 'xr': [], 'dfbot': [], 'var': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [],
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
        'dfzoo': get_text(entry_el, 'dfzoo'),
        'nag': get_text(entry_el, 'nag'),
        'dfn': get_text(entry_el, 'dfn'),
        'sem': get_text(entry_el, 'sem'),
        'emp': get_text(entry_el, 'emp'),
        'ton': get_text(entry_el, 'ton'),
        # arrays
        'phr': [], 'gram': [], 'xr': [], 'dfbot': [], 'var': [], 'so': [], 'rec': [], 'nb': [], 'nbi': [],
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


def compute_nav_structure(groups):
    """Partition hdr groups into bigram sub-sections, preserving entry order.
    Returns a list of nav items, each with keys: tok, label, is_vowel, subs.
    Each sub has: sub_id, label, entries."""
    nav = []
    for tok, meta in groups.items():
        label   = meta['label']
        entries = meta['entries']
        r_label = trans_str(label) if label else ''
        is_vowel = bool(r_label and r_label[0] in _NAV_VOWELS)

        if is_vowel:
            nav.append({'tok': tok, 'label': label, 'is_vowel': True,
                        'subs': [{'sub_id': f'section-{tok}', 'label': label, 'entries': entries}]})
            continue

        bg_order, bg_entries, last_bg, dollar_buf = [], {}, None, []
        for entry in entries:
            hw = entry.get('hw', '')
            if hw.startswith('$'):
                dollar_buf.append(entry); continue
            bg = _nav_bigram(hw)
            if bg is None: continue
            if dollar_buf and last_bg:
                bg_entries[last_bg].extend(dollar_buf); dollar_buf = []
            if bg not in bg_entries:
                bg_order.append(bg); bg_entries[bg] = []
            bg_entries[bg].append(entry)
            last_bg = bg
        if dollar_buf and last_bg:
            bg_entries[last_bg].extend(dollar_buf)

        subs = [{'sub_id': f'section-{tok}-{i}', 'label': bg, 'entries': bg_entries[bg]}
                for i, bg in enumerate(bg_order)]
        if not subs:
            subs = [{'sub_id': f'section-{tok}', 'label': label, 'entries': entries}]
        nav.append({'tok': tok, 'label': label, 'is_vowel': False, 'subs': subs})
    return nav


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

    return groups, i

# =================== rendering ===================

def render_lang_lines(ps, nag, dfn, dff, dfe, dfbot):
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
    for d in dfbot:
        if d: lines.append(f'<span class="small-caps">bot</span> <span class="xxx">{render_dfbot(d)}</span>')
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
    for xr in d.get('xr', []):
        xr2 = render_2part(xr)
        if xr2:
            parts.append(f"<div class='mb-1'><i>cf </i> {xr2}</div>")
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
    lines = render_lang_lines('', m.get('nag', ''), m.get('dfn', ''), m.get('dff', ''), m.get('dfe', ''), m.get('dfbot', []))
    short_html = ""
    if lines:
        short_html = f"""
        <div class="mode-short">
          {badge_html}
          <div class="mode-sub"><p class="mb-0">{lines}</p></div>
        </div>"""
    long_bits = render_long_bits(m)
    head_bits = ""
    long_html = f"""
      <div class="mode-long" id="{mid}-long" style="display:none;">
        <div class="mode-body">{head_bits}{long_bits}</div>
      </div>""" if head_bits or long_bits else ''
    return f"<div class='mode-sub'>{short_html}{long_html}</div>"

def render_sub_block(s):
    sid = s['id']
    if not s.get('hw'):
        print('skipped subheadword article (no proper hw found)', sid)
        return ''
    head_html = render_hw_etc(s)
    lines = render_lang_lines('', s.get('nag',''), s.get('dfn',''), s.get('dff',''), s.get('dfe',''), s.get('dfbot', []))
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
      </div>""" if long_bits else ''
    mode_blocks = ''.join(render_mode_block(m) for m in s.get('modes', []))
    return f"<div class='mode-block'>{short_html}{long_html}{mode_blocks}</div>"

def render_hw_etc(entry):
    hw = entry.get('hw', None)
    homonym = re.match(r'([^\s]+)\$(.*)', hw)
    ps_html = f'&#160;<i class="small-caps">{esc(entry["ps"])}</i>' if entry.get('ps') else ''
    cf_html = render_cf(entry.get('cf', None))
    emp_html = render_emp(entry.get('emp', None))
    var_html = ''.join([render_var(var)for var in entry.get('var', [])])
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
        if entry.get('dff') or entry.get('dfe') or entry.get('nag') or entry.get('dfn') or entry.get('dfbot', []):
            pseudo = {
                'id': f"{entry['id']}-m0",
                'level': None,
                'nag': entry.get('nag',''), 'dfn': entry.get('dfn',''),
                'dff': entry.get('dff',''), 'dfe': entry.get('dfe',''),
                'sem': entry.get('sem',''),
                'var': entry.get('var',''),
                'phr': entry.get('phr',[]), 'gram': entry.get('gram',[]), 'xr': entry.get('xr',[]), 'dfbot': entry.get('dfbot', []),
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
        lines = render_lang_lines('', entry.get('nag',''), entry.get('dfn',''), entry.get('dff',''), entry.get('dfe',''), entry.get('dfbot', []))
        body = f"<p class='mb-0'>{lines}</p>" if lines else ""
    return f"<div class='short'>{head}{body}</div>"

def render_entry_long(entry):
    has_base_defs = entry.get('dff') or entry.get('dfe') or entry.get('nag') or entry.get('dfn') or entry.get('dfbot', [])
    if (entry.get('modes') or entry.get('subs')) and has_base_defs:
        d_extras_html = ''
    else:
        d_extras_html = render_long_bits(entry)
    return d_extras_html

def create_html():
    STYLE = r"""
:root { --font-sans: system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
html, body { height: 100%; }
body { font-family: var(--font-sans); margin: 0; display: grid; grid-template-rows: auto 1fr; height: 100vh; overflow: hidden; }
.fixed-topbar { position: relative; z-index: 1000; background: #fff; box-shadow: 0 1px 0 rgba(0,0,0,.06); overflow-x: hidden; width: 100%; overflow: visible; } 
#views { padding-top: 4px ; min-height: 0; overflow: auto; -webkit-overflow-scrolling: touch; }
#views > * { display: none !important; }
.small-caps { font-variant-caps: small-caps; font-size: .7rem; }
.small { font-size: .7rem; }
.mb-0 { margin-bottom: 0; }
.mb-1 { margin-bottom: 4px; }
.my-2 { margin: 6px 0 6px 0; }
.ms-1 { margin-left: .25rem; }
.header { position: sticky; z-index: 2; display: flex; align-items: center; gap: .75rem; background: #A51931; color: #fff; width: 100%; padding: 0.3rem; box-sizing: border-box; }
.header .logo { width: 48px; height: 48px; flex: 0 0 auto; }
/* .header .logo img { display: block; width: 100%; height: 100%; object-fit: contain; object-position: center; } */
.header .logo svg, .header .logo img { width: 100%; height: 100%; display: block; }
.header .brand { color: #fff; text-decoration: none; font-weight: bold; overflow: hidden; }
.header .page-links { margin-left: auto; display: flex; gap: .5rem; }
.header .page-links a { color: #fff; text-decoration: none; padding: .25rem .5rem; border-radius: .375rem; }
.header .page-links a:hover { background: rgba(255,255,255,.18); }
/* Hamburger (CSS-only) */
.menu-toggle { position: absolute; opacity: 0; width: 0; height: 0; pointer-events: none; }
.hamburger { display: none; cursor: pointer; margin-left: auto; padding: .25rem; z-index: 1300; }
.hamburger span { display: block; width: 24px; height: 2px; background: #fff; margin: 5px 0; border-radius: 1px; }
 .to-dico { display: none; }
/* Mobile: dropdown menu, etc. */
@media (max-width: 768px) {
 .hamburger { display: block; flex: 0 0 auto; margin-left: .5rem; }
 .header .brand { flex: 1 1 auto; min-width: 0; font-size:.70rem;}
 .header .page-links { display: none; position: absolute; top: 100%; left: 0; right: 0; z-index: 1200; background: #fff; border: 1px solid #e5e7eb; padding: .5rem; }
 .header .page-links a { display: block; color: #111; text-decoration: none; padding: .5rem .75rem; border-radius: .375rem; }
 .header .page-links a:hover { background: #f2f2f2; }
  .to-dico { display: block; }
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
#sub-nav { overflow-x: auto; border-top: 1px solid #e5e7eb; background: #f1f5ff; }
.sub-nav-row { display: flex; flex-wrap: nowrap; padding: .2rem .5rem; gap: .15rem; }
.sub-nav-link { flex: 0 0 auto; font-size: 1rem; padding: .15rem .45rem; color: #0d6efd; text-decoration: none; border: 1px solid transparent; border-radius: .375rem; white-space: nowrap; }
.sub-nav-link:hover { background: rgba(13,110,253,.08); border-color: rgba(13,110,253,.2); }
.sub-nav-link.active { color: #fff; background: #0d6efd; border-color: #0d6efd; }
body.show-dico .searchnav { display: block !important; }
body.show-about #page-about { display: block !important; }
body.show-credits #page-credits { display: block !important; }
body.show-guide #page-guide { display: block !important; }
body.show-dico #dictionary { display: block !important; }
#page-about { display: block; }
.page { position: relative; margin: 0 auto 1rem; padding: 0 0.4rem; background: #fff; border: 1px solid #e5e7eb; border-radius: .5rem; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
.page .to-dico { float: right; top: .75rem; right: .75rem; font-size: .9rem; padding: .35rem .7rem; margin: .2rem; background: #fff; border: 1px solid #ced4da; border-radius: .375rem; text-decoration: none; color: inherit; }
.page .to-dico:hover { background: #f1f3f5; }
dt { font-weight: bold; font-style: italic; }
/* Entries */
.letter-section { padding-bottom: 4rem; }
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
.mode-short { padding: .25rem 0; border-top: 1px dashed #eee; }
.mode-short:first-child { border-top: none; }
.badge.text-bg-secondary { background: #6c757d; color: #fff; }
/* Search results */
#search-results mark { background: #fff3cd; padding: 0 .1em; }
#search-results .long, #search-results .mode-long { display: none; }
/* Wrapping / Gloss layout */
.mode-body p, .mode-sub p { margin: .15rem 0 0; text-indent: 0; }
.mode-body p .small-caps, .mode-sub p .small-caps { display: inline-block; text-align: left; }
.mode-body p .dfn, .mode-sub p .dfn { margin-left: .35em; }
/* Responsive tweaks */
@media (max-width: 600px) {
  .mode-sub p .small-caps, .mode-body p .small-caps { min-width: 2.2em; }
 }
@media (max-width: 576px) {
  html { font-size: 16px; }
  .header .brand { font-size: .7rem; }
  #letter-nav .nav-link { font-size: 1.0rem; padding: .2rem; }
  .short p, .long { font-size: .9rem; line-height: 1.2; }
 }
.page h4 { font-size: 1.15rem; margin: .75rem 0 .3rem; }
.page h5 { font-size: 1rem; font-weight: 600; margin: .6rem 0 .2rem; }
.page p, .page dd, .page li { font-size: .9rem; line-height: 1.5; }
table { border-collapse: collapse; width: 100%; }
tr, td, th { border: 1px solid; }
td, th { padding: .2rem .4rem; }
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

// ----- Letter navigation -----
function hideSubNav(){
  const sn = document.getElementById('sub-nav');
  if (!sn) return;
  sn.style.display = 'none';
  sn.querySelectorAll('.sub-nav-row').forEach(r => r.style.display = 'none');
}
// showToken: used for vowel letters (direct section link)
function showToken(sectionId, linkEl){
  hideSubNav();
  document.querySelectorAll('.letter-section').forEach(s => s.style.display = 'none');
  const sec = document.getElementById(sectionId);
  if (sec) sec.style.display = 'block';
  document.querySelectorAll('#letter-nav .nav-link').forEach(a => a.classList.remove('active'));
  if (linkEl) linkEl.classList.add('active');
  const sr = document.getElementById('search-results'); if (sr) sr.style.display = 'none';
  return false;
}
// toggleSubNav: used for consonant letters with sub-sections
function toggleSubNav(tok, btn){
  const sn   = document.getElementById('sub-nav');
  const row  = document.getElementById('subnav-' + tok);
  const alreadyOpen = sn && sn.style.display !== 'none' && row && row.style.display === 'flex';
  hideSubNav();
  document.querySelectorAll('#letter-nav .nav-link').forEach(a => a.classList.remove('active'));
  if (!alreadyOpen){
    if (sn)  sn.style.display  = 'block';
    if (row) row.style.display = 'flex';
    btn.classList.add('active');
    const firstSub = row && row.querySelector('.sub-nav-link');
    if (firstSub) firstSub.click();
  }
  return false;
}
// showSubSection: used by sub-letter links
function showSubSection(sectionId, linkEl){
  document.querySelectorAll('.letter-section').forEach(s => s.style.display = 'none');
  const sec = document.getElementById(sectionId);
  if (sec) sec.style.display = 'block';
  document.querySelectorAll('.sub-nav-link').forEach(a => a.classList.remove('active'));
  if (linkEl) linkEl.classList.add('active');
  const sr = document.getElementById('search-results'); if (sr) sr.style.display = 'none';
  const navBar = document.getElementById('letter-nav'); if (navBar) navBar.style.display = 'none';
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
  hideSubNav();
  hideAllSections();
  const first = document.querySelector('.letter-section'); if (first) first.style.display = 'block';
  document.querySelectorAll('#letter-nav .nav-link').forEach(a => a.classList.remove('active'));
  const firstLink = document.querySelector('#letter-nav .nav-link'); if (firstLink) firstLink.classList.add('active');
  return false;
}
// ==================================================
// Keyword Search (whole-word), as written by ChatGPT
// ==================================================

// ---- Config ----
const KEYWORD_MODE = 'AND';   // 'AND' or 'OR'
const MIN_TERM_LEN = 1;       // <-- allow single-character terms
const MAX_RESULTS = 1500;     // perf guard for very small terms

// ---- Utilities ----
function escRegex(s){ return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

// Build one regex per term.
// We generate:
//  - searchRx: whole-word-ish match without lookbehind (Safari-safe) using Unicode properties when available
//  - hiRx: plain term match for highlighting (keeps existing highlight behavior reliable)
function buildTermRegexes(query){
  const raw = (query || '').trim();
  // Treat the entire query as a single phrase (do NOT split into separate terms).
  // Convert runs of whitespace in the query into a flexible whitespace matcher.
  const tokens = raw.split(/\s+/).filter(Boolean);
  const core = tokens.map(t => escRegex(t)).join('\\s+');

  if (!core || core.replace(/\\s\+/g, '').length < MIN_TERM_LEN) return [];

  // Whole-phrase, whole-word boundaries (Unicode-aware when possible; no lookbehind).
  // We keep a capturing group for the phrase so highlighting can wrap only the phrase,
  // not the boundary character.
  let searchRx, hiRx;
  try {
    const pat = `(^|[^\\p{L}\\p{M}\\p{Nd}])(${core})(?=$|[^\\p{L}\\p{M}\\p{Nd}])`;
    searchRx = new RegExp(pat, 'iu');
    hiRx     = new RegExp(pat, 'giu');
  } catch (e) {
    const pat = `(^|[^A-Za-z0-9_])(${core})(?=$|[^A-Za-z0-9_])`;
    searchRx = new RegExp(pat, 'i');
    hiRx     = new RegExp(pat, 'gi');
  }

  return [{ searchRx, hiRx }];
}


// AND/OR evaluation against plain text (uses searchRx only)
function textIncludesByMode(text, rxObjs){
  if (!rxObjs.length) return false;
  if (KEYWORD_MODE === 'OR') return rxObjs.some(o => o.searchRx.test(text));
  return rxObjs.every(o => o.searchRx.test(text));
}

// Remove previous highlights
function clearMarks(el){
  el.querySelectorAll('mark.hl').forEach(m => {
    const p = m.parentNode;
    while (m.firstChild) p.insertBefore(m.firstChild, m);
    p.removeChild(m);
  });
}

// Replace a single text node with a fragment that wraps matches in <mark>
function highlightNode(node, rx){
  const txt = node.nodeValue;
  rx.lastIndex = 0;
  let m, last = 0, found = false, count = 0;
  const frag = document.createDocumentFragment();

  while ((m = rx.exec(txt))){
    // Two possible shapes:
    //  1) Unicode-aware: m[0] is the match we want to highlight.
    //  2) Fallback boundary: m[1] is the delimiter (or ''), m[2] is the term to highlight.
    if (m.length >= 3 && typeof m[2] === 'string'){
      const prefixLen = (m[1] || '').length;
      const termText = m[2];
      const termStart = m.index + prefixLen;

      if (m.index > last) frag.appendChild(document.createTextNode(txt.slice(last, m.index)));
      if (prefixLen) frag.appendChild(document.createTextNode(txt.slice(m.index, termStart)));

      const mark = document.createElement('mark'); mark.className = 'hl';
      mark.textContent = termText;
      frag.appendChild(mark);

      last = termStart + termText.length;
    } else {
      const matchText = m[0] || '';
      if (m.index > last) frag.appendChild(document.createTextNode(txt.slice(last, m.index)));

      const mark = document.createElement('mark'); mark.className = 'hl';
      mark.textContent = matchText;
      frag.appendChild(mark);

      last = m.index + matchText.length;
    }

    // safety against zero-length progress
    if (rx.lastIndex === m.index) rx.lastIndex++;
    found = true;
    if (++count > MAX_RESULTS) break;
  }
  if (!found) return;
  if (last < txt.length) frag.appendChild(document.createTextNode(txt.slice(last)));
  node.parentNode.replaceChild(frag, node);
}

function highlightInElementMulti(el, regexes){
  if (!el || !regexes.length) return;
  clearMarks(el);

  const getTextNodes = () => {
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {
      acceptNode(n){
        if (!n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const p = n.parentNode;
        if (p && /^(SCRIPT|STYLE)$/i.test(p.tagName)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    const out = [];
    while (w.nextNode()) out.push(w.currentNode);
    return out;
  };

  for (const rx of regexes){
    const nodes = getTextNodes();  // fresh list each pass (DOM mutates)
    for (const node of nodes) highlightNode(node, rx);
  }
}

// =======================

function getSearchText(el){
  if (!el) return '';
  const clone = el.cloneNode(true);
  clone.querySelectorAll('.small-caps').forEach(sc => sc.remove());
  clone.querySelectorAll('br,hr').forEach(b => b.replaceWith(' '));
  clone.querySelectorAll('p,div,li,ul,ol,dl,dt,dd,table,thead,tbody,tfoot,tr,td,th,section,article,header,footer,aside,nav,h1,h2,h3,h4,h5,h6,pre,blockquote').forEach(b => { b.prepend(' '); b.append(' '); });
  return clone.textContent.replace(/\s+/g, ' ').trim();
}

function entrySearchText(entry){
  if (!entry) return '';
  const short = getSearchText(entry.querySelector('.short'));
  const long  = getSearchText(entry.querySelector('.long'));
  return short + (long ? ' ' + long : '');
}

// Drop-in replacement for your handleSearch()
// =======================
function handleSearch(input){
  const q = (input && input.value ? input.value : '').trim();
  const resultsDiv = document.getElementById('search-results'); if (!resultsDiv) return;
  const navBar = document.getElementById('letter-nav');

  resultsDiv.innerHTML = '';
  if (q.length === 0){ resetSearch(); return; }

  const regexes = buildTermRegexes(q);
  if (!regexes.length){
    if (navBar) navBar.style.display = 'none';
    hideAllSections();
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = '<p class="small">Type one or more keywords.</p>';
    return;
  }

  if (navBar) navBar.style.display = 'none';
  hideAllSections();
  resultsDiv.style.display = 'block';

  let appended = 0;
  document.querySelectorAll('.entry').forEach(entry => {
    const hay = entrySearchText(entry);
    if (textIncludesByMode(hay, regexes)){
      const clone = entry.cloneNode(true);
      clone.querySelectorAll('[id]').forEach(n => n.removeAttribute('id'));
      // In search results, always show any hidden/long content so highlights are visible.
      clone.querySelectorAll('.long, .mode-long').forEach(n => n.style.display = 'block');
      clone.classList.add('expanded');
      resultsDiv.appendChild(clone);
      highlightInElementMulti(clone, regexes.map(o => o.hiRx));
      if (++appended > MAX_RESULTS){ /* optional: show a cap notice */ }
    }
  });

  if (resultsDiv.children.length === 0){
    resultsDiv.innerHTML = '<p class="small">No results found.</p>';
  }
}

window.debouncedSearch = debounce(handleSearch, 80);


// ----- Page mode (About / Credits / Dictionary) + hamburger auto-close -----
(function () {
  function setPageFromHash(){
    const h = (location.hash || '#about').toLowerCase();
    const b = document.body.classList;
    b.remove('show-about','show-credits','show-guide','show-dico');
    if (h === '#credits')      b.add('show-credits');
    else if (h === '#guide')   b.add('show-guide');
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

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/tmg/sw.js");
}
"""

    HTML_SHELL = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<link rel="manifest" href="/tmg/manifest.json">
<link rel="apple-touch-icon" href="/tmg/icons/apple-touch-icon-180.png">
<meta name="theme-color" content="#ffffff">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>{title}</title>
<style type="text/css">{style}</style>
</head>
<body>

<div class="fixed-topbar">
  <header class="header">
    <!-- div class="logo" aria-hidden="true"> + LOGO + </div -->
    <a class="brand" href="#dico">{title}</a>

    <input type="checkbox" id="menu-toggle" class="menu-toggle" />
    <label for="menu-toggle" class="hamburger" aria-label="Menu">
      <span></span><span></span><span></span>
    </label>

    <nav class="page-links">
      <a href="#about">About</a>
      <a href="#credits">Credits</a>
      <a href="#guide">Guide</a>
      <a href="#dico">To Dictionary</a>
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
    """ + ABOUT + """
        <p>This edition was created on {run_date}.
    </section>
    <section id="page-credits" class="page">
    """ + CREDITS + """
    </section>
    <section id="page-guide" class="page">
    """ + GUIDE + """
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
    return HTML_SHELL, STYLE, SCRIPT

def build_letter_nav(nav_structure):
    links = []
    sub_rows = []
    first = True
    for item in nav_structure:
        tok, label, subs = item['tok'], item['label'], item['subs']
        active = ' active' if first else ''
        first = False
        if item['is_vowel'] or len(subs) == 1:
            sec_id = subs[0]['sub_id']
            links.append(
                f'<a class="nav-link{active}" data-token="{tok}" href="#"'
                f' onclick="return showToken(\'{sec_id}\',this)">{label}</a>'
            )
        else:
            links.append(
                f'<a class="nav-link has-subs{active}" data-token="{tok}" href="#"'
                f' onclick="return toggleSubNav(\'{tok}\',this)">{label}</a>'
            )
            sub_links = ''.join(
                f'<a class="sub-nav-link" href="#"'
                f' onclick="return showSubSection(\'{s["sub_id"]}\',this)">{s["label"]}</a>'
                for s in subs
            )
            sub_rows.append(f'<div id="subnav-{tok}" class="sub-nav-row">{sub_links}</div>')
    nav_html = '<nav id="letter-nav">' + ''.join(links) + '</nav>'
    sub_nav_html = '<div id="sub-nav" style="display:none;">' + ''.join(sub_rows) + '</div>'
    return nav_html + sub_nav_html


def build_sections(nav_structure):
    out = []
    first = True
    for item in nav_structure:
        for sub in item['subs']:
            disp = '' if first else ' style="display:none;"'
            first = False
            entry_html = []
            for e in sub['entries']:
                eid = e['id']
                short_html = render_short(e)
                long_html = render_entry_long(e)
                long_block = (
                    f"<div class='long' id='{eid}-long' style='display:none;'>{long_html}</div>"
                    if long_html else ''
                )
                has_more = bool(long_html or 'mode-long' in short_html)
                cls = "entry has-more" if has_more else "entry"
                entry_html.append(
                    f"<div id='{eid}' class='{cls}' onclick=\"return toggleEntryAll('{eid}')\">{short_html}{long_block}</div>"
                )
            out.append(f"<div class='letter-section' id='{sub['sub_id']}'{disp}>" + ''.join(entry_html) + "</div>")
    return ''.join(out)

def minify_html(s: str) -> str:
    s = re.sub(r'<!--.*?-->', '', s, flags=re.DOTALL)
    s = re.sub(r'> +<', '> <', s)
    return s.strip()

def render_html(groups, title, ENTRY_COUNT, HTML_SHELL, STYLE, SCRIPT):
    nav_structure = compute_nav_structure(groups)
    return HTML_SHELL.format(
        title=esc(title),
        style=STYLE,
        script=SCRIPT,
        letter_nav=build_letter_nav(nav_structure),
        sections=build_sections(nav_structure),
        run_date=time.strftime("%Y-%m-%d at %H:%M:%S UTC", time.gmtime()),
        entry_count=ENTRY_COUNT
    )

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Render dictionary XML to standalone HTML (modes + subs), grouped by <hdr>.")
    ap.add_argument("xml", help="Input XML file")
    ap.add_argument("-a", "--about", default="tamang_about.html", help="About HTML file")
    ap.add_argument("-g", "--guide", default="tamang_guide.html", help="User Guide HTML file")
    ap.add_argument("-c", "--credits", default="tamang_credits.html", help="Credits HTML file")
    ap.add_argument("-l", "--logo", default="tamang_logo.svg", help="Logo SVG file")
    ap.add_argument("-o", "--out", default="TamangDictionary.html", help="Output HTML file")
    ap.add_argument("--title", default="Tamang | Nepali – French – English Dictionary", help="Page title")
    ap.add_argument("--no-minify", action="store_true", help="Skip HTML minification")
    args = ap.parse_args()
    ABOUT = Path(args.about).read_text(encoding="utf-8")
    GUIDE = Path(args.guide).read_text(encoding="utf-8")
    CREDITS = Path(args.credits).read_text(encoding="utf-8")
    LOGO = Path(args.logo).read_text(encoding="utf-8")
    HTML_SHELL, STYLE, SCRIPT = create_html()

    groups, ENTRY_COUNT = parse_entries_from_file(args.xml)
    html = render_html(groups, args.title, ENTRY_COUNT, HTML_SHELL, STYLE, SCRIPT)
    if not args.no_minify:
        html = minify_html(html)
    Path(args.out).write_text(html, encoding="utf-8")
    print(f"✅ Wrote {args.out}")
