import read
import utils
from RE import Statistics
coverage_statistics = Statistics()


# Coverage utilities
def check_mel_coverage(settings):
    mel_glosses = set()
    all_matched = 0
    all_not_matched = 0
    all_forms = 0
    glosses_not_matched_by_language = {}
    unmatched_glosses = set()
    number_of_mels = 0
    for mel in read.read_mel_file(settings.mel_filename):
        mel_glosses = mel_glosses.union(mel.glosses)
        number_of_mels += 1
    attested_lexicons = read.read_attested_lexicons(settings)
    unused_mel_glosses = dict([(x, '') for x in mel_glosses])
    for language in attested_lexicons:
        glosses_not_matched_by_language[language] = set()
        matched = 0
        not_matched = 0
        forms = len(attested_lexicons[language].forms)
        for gloss in utils.glosses_by_language(attested_lexicons[language]):
            if gloss not in mel_glosses:
                not_matched += 1
                glosses_not_matched_by_language[language].add(gloss)
                unmatched_glosses.add(gloss)
                # print(f'{language} {gloss}')
            else:
                matched += 1
                try:
                    del unused_mel_glosses[gloss]
                except:
                    pass
        print(f'{language}: {matched + not_matched} distinct glosses, {matched} matched, {not_matched} did not match, {forms} forms')
        coverage_statistics.language_stats[language] = {
            'distinct_glosses': matched + not_matched,
            'matched': matched,
            'not_matched': not_matched,
            'forms': forms
        }
        all_matched += matched
        all_not_matched += not_matched
        all_forms += forms
    unused_mels = len(unused_mel_glosses)

    coverage_statistics.matched = all_matched
    coverage_statistics.not_matched = all_not_matched
    coverage_statistics.forms = all_forms
    coverage_statistics.unused_mels = unused_mels
    coverage_statistics.number_of_mels = number_of_mels
    coverage_statistics.mel_glosses = mel_glosses
    coverage_statistics.unmatched_by_language = glosses_not_matched_by_language
    coverage_statistics.unmatched_glosses = unmatched_glosses

    print(f'\nmel summary: mels {number_of_mels} mel glosses {len(mel_glosses)} unused mel glosses {unused_mels}')
    print(f'gloss summary: {all_matched + all_not_matched} distinct glosses, {all_matched} matched, {all_not_matched} did not match, {all_forms} forms')
    # for language in glosses_not_matched_by_language:
    #
    #     if len(glosses_not_matched_by_language[language]) > 0:
    #         print(language)
    #         print(glosses_not_matched_by_language[language])

    return coverage_statistics
