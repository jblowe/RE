# Misc. utils
def all_glosses(lexicon):
    glosses = set()
    for form in lexicon.forms:
        if form.gloss:
            glosses.add(form.gloss)
    return glosses
