import os
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

# based on https://stackoverflow.com/questions/12451531/python-try-catch-block-inside-lambda
def tryconvert(value, *types):
    for t in types:
        try:
            return t(value)
        except (ValueError, TypeError):
            continue
    return value
