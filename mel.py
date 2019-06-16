import re

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

def associated_mels(mels, gloss):
    '''Return all mels which contain gloss.'''
    if mels is None:
        return [default_mel]
    associated = [mel for mel in mels if search_mels(gloss, mel.glosses)]
    return associated if associated else [default_mel]

def search_mels(gloss, mel_glosses):
    return (gloss in mel_glosses or
            any((mel_gloss in gloss for mel_gloss in mel_glosses if gloss is not None)))
