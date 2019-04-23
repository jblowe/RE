import read
import utils

# Coverage utilities
def check_mel_coverage(settings):
    mel_glosses = set()
    for mel in read.read_mel_file(settings.mel_filename):
        mel_glosses.union(mel.glosses)
    for gloss in utils.all_glosses(read.read_attested_lexicons(settings)):
        if gloss not in mel_glosses:
            print(f'{gloss}')
