import os
import re
from contextlib import contextmanager

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
    return candidates


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
