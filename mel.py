import re
import collections

class Mel:
    def __init__(self, glosses, id):
        self.glosses = glosses
        self.id = id
        
    def __repr__(self):
        return f'<Mel({self.id}, {self.glosses})>'

    def __str__(self):
        return f'mel {self.id}: [{self.glosses[0]}])>'

class DefaultMel(Mel):
    def __repr__(self):
        return '<DefaultMel>'

    def __str__(self):
        return 'No mel'

default_mel = DefaultMel([], '')

def compile_associated_mels(mels, glosses):
    '''Compile a mapping of glosses to mels.'''
    if mels is None:
        return None
    association = collections.defaultdict(set)
    for mel in mels:
        for gloss in mel.glosses:
            association[gloss].add(mel)
        for gloss in glosses:
            if search_mels(gloss, mel.glosses):
                association[gloss].add(mel)
    return association

def associated_mels(association, gloss):
    '''Lookup gloss in the table of MEL associations.'''
    if association is None:
        return [default_mel]
    return list(association.get(gloss, [default_mel]))

def search_mels(gloss, mel_glosses):
    return any((mel_gloss in gloss for mel_gloss in mel_glosses))
