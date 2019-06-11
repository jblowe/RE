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

