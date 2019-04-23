# Misc. utils
def all_glosses(attested_lexicons):
    glosses = set()
    for lexicon in attested_lexicons.values():
        for form in lexicon.forms:
            if form.gloss:
                glosses.add(form.gloss)
    return glosses
