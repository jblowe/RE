import os
import re
import unicodedata
from contextlib import contextmanager

def nfc(s):
    """Normalize *s* to NFC Unicode form.  Returns None unchanged."""
    return unicodedata.normalize('NFC', s) if s is not None else None

def nfd(s):
    """Normalize *s* to NFD Unicode form.  Returns None unchanged."""
    return unicodedata.normalize('NFD', s) if s is not None else None

# Misc. utils
def all_glosses(lexicons):
    glosses = set()
    for language in lexicons:
        for form in lexicons[language].forms:
            if form.gloss:
                glosses.add(form.gloss)
    return glosses


def glosses_by_language(single_lexicon):
    glosses = set()
    for form in single_lexicon.forms:
        if form.gloss:
            glosses.add(form.gloss)
    return glosses

## A pale imitation of unwind-protect wrapped in a `with' macro.
@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

# Natural sorting, so that e.g. c102 appears after c2.
def natural_sort_key(s, _nsre=re.compile(r'(\d+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]

# based on https://stackoverflow.com/questions/12451531/python-try-catch-block-inside-lambda
def tryconvert(value, *types):
    for t in types:
        try:
            return t(value)
        except (ValueError, TypeError):
            continue
    return value


def split_csv(s):
    if s is None:
        return None
    return [p.strip() for p in s.split(',') if p.strip()]


# ── Supra-segmental spec helpers ──────────────────────────────────────────────
# The <spec> XML attribute may be stored either as a literal comma-separated
# string (e.g. "ˊ,ˋ") or as a sequence of Unicode codepoint tokens
# (e.g. "U+0303" or "U+0303, U+0308").  The two helpers below handle both
# directions of the conversion.

import re as _re

_CODEPOINT_RE = _re.compile(
    r'^\s*U\+[0-9A-Fa-f]{4,6}(\s*[,\s]\s*U\+[0-9A-Fa-f]{4,6})*\s*$',
    _re.IGNORECASE,
)


def parse_spec_value(s):
    """Convert a spec string to a list of individual Unicode character strings.

    Accepts one of two formats (but NOT a mix):

    1. A comma- (or whitespace-) separated sequence of Unicode codepoints,
       e.g. ``U+0303`` or ``U+0303, U+0308``.
    2. A literal comma-separated string, e.g. ``ˊ,ˋ`` or ``ˈ``.

    In format 1 each token is converted to its actual Unicode character.
    In format 2 the string is split on commas and each non-empty piece is
    returned as-is (just stripped of leading/trailing whitespace).
    """
    s = s.strip()
    if not s:
        return []
    if _CODEPOINT_RE.match(s):
        return [chr(int(cp, 16))
                for cp in _re.findall(r'U\+([0-9A-Fa-f]{4,6})', s, _re.IGNORECASE)]
    return [part.strip() for part in s.split(',') if part.strip()]


def spec_display(chars):
    """Render a supra_segmentals list as a human-readable display/storage string.

    Printable, non-combining characters are shown as-is (e.g. ``ˈ``).
    Combining marks (Unicode category M*) and other non-printable characters
    are shown in ``U+XXXX`` notation so they remain visible in UI fields and
    text editors.

    This is the inverse of :func:`parse_spec_value`:
    ``parse_spec_value(spec_display(chars)) == chars`` for any valid list.

    Prefer :func:`spec_for_storage` when you have a :class:`RE.SyllableCanon`
    object — it preserves the original user notation verbatim.
    """
    parts = []
    for ch in chars:
        if not ch:
            continue
        cat = unicodedata.category(ch)
        if cat.startswith('M') or not ch.isprintable():
            parts.append(f'U+{ord(ch):04X}')
        else:
            parts.append(ch)
    return ','.join(parts)


def spec_for_storage(syllable_canon):
    """Return the spec string that should be written to XML for *syllable_canon*.

    If the canon carries a ``raw_spec`` string (set when the canon was read
    from XML), that string is returned verbatim so the user's original
    notation — whether literal ``ˈ`` or codepoint ``U+0303`` — is preserved
    exactly.  Otherwise falls back to :func:`spec_display`.
    """
    if getattr(syllable_canon, 'raw_spec', None) is not None:
        return syllable_canon.raw_spec
    return spec_display(syllable_canon.supra_segmentals)


def list_attested_languages(project_path):
    """Return language codes for files matching ....<LANG>.data.xml"""
    langs = []
    for fn in sorted(os.listdir(project_path)):
        pattern = re.compile(r'^(?:[^.]+\.)?([^.]+)\.data\.xml$')
        m = pattern.match(fn)
        if m:
            # print(fn, "→", m.group(1))
            langs.append(m.group(1))
        else:
            pass
    return langs

def resolve_file(project_path, project_code, token, suffix):
    """Resolve a token to a filename in a project directory."""
    if token is None:
        return None
    for root, dirs, files in os.walk(project_path):
        for f in files:
            if f == f'{token}{suffix}' or f.endswith(f'.{token}{suffix}'):
                return(os.path.join(root, f))
    return None

def find_candidates(project_path, suffix):
    """find all candidate files with the specified suffix."""
    candidates = []
    for root, dirs, files in os.walk(project_path):
        for f in files:
            if f.endswith(suffix):
                pattern = re.compile(rf'^(?:[^.]+\.)?([^.]+).{suffix}$')
                m = pattern.match(f)
                if m:
                    # print(f, "→", m.group(1))
                    candidates.append(m.group(1))
    return sorted(candidates)


def read_protolanguage_from_correspondences(full_path):
    """Try to find <protolanguage>...</protolanguage> in a correspondences file."""
    try:
        import xml.etree.ElementTree as ET
        root = ET.parse(full_path).getroot()
        # allow either <protolanguage> or <protoLanguage>
        el = root.find('protolanguage')
        if el is not None and (el.text or '').strip():
            return el.text.strip()
    except Exception:
        pass
    return None
