# Misc. utils
def all_glosses(lexicon):
    glosses = set()
    for language in lexicon:
        for form in lexicon[language].forms:
            if form.gloss:
                glosses.add(form.gloss)
    return glosses
