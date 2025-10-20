import read
import utils
from mel import search_mels
from RE import Statistics
from collections import Counter, defaultdict


# Coverage utilities
def check_mel_coverage(settings):
    coverage_statistics = Statistics()
    mel_glosses = set()
    all_matched = 0
    all_not_matched = 0
    all_forms = 0
    glosses_not_matched_by_language = {}
    unmatched_glosses = set()
    matched_glosses = set()
    mel_usage = {}
    number_of_mels = 0
    mels = read.read_mel_file(settings.mel_filename)
    for mel in mels:
        mel_glosses = mel_glosses.union(mel.glosses)
        mel_usage[mel.id] = {}
        number_of_mels += 1
    attested_lexicons = read.read_attested_lexicons(settings)
    mel_stats = Counter()
    # dict([(x, 0) for x in mel_glosses])
    glosses = Counter()
    for language in attested_lexicons:
        glosses_not_matched_by_language[language] = set()
        matched = 0
        not_matched = 0
        forms = len(attested_lexicons[language].forms)
        for gloss in utils.glosses_by_language(attested_lexicons[language]):
            glosses[gloss] += 1
            if 'daughter in law' in gloss:
                pass
            matched_terms = search_mels(gloss, mel_glosses)
            if len(matched_terms) != 0:
                matched += 1
                matched_glosses.add(gloss)
                # mel_stats[gloss] += 1
                for g in matched_terms:
                    mel_stats[g] += 1
            else:
                not_matched += 1
                glosses_not_matched_by_language[language].add(gloss)
                unmatched_glosses.add(gloss)
                # print(f'{language} {gloss}')

        print(f'{language}: {matched + not_matched} distinct glosses, {matched} matched, {not_matched} did not match, {forms} forms')
        coverage_statistics.language_stats[language] = {
            'input_glosses': matched + not_matched,
            'matched': matched,
            'not_matched': not_matched,
            'forms': forms
        }
        all_matched += matched
        all_not_matched += not_matched
        all_forms += forms

    for mel in mels:
        used = 0
        for gloss in mel.glosses:
            used += mel_stats[gloss]
            mel_usage[mel.id][gloss] = mel_stats[gloss]
        mel_usage[mel.id]['usage'] = True if used > 0 else False

    unused_mels = Counter([mel_usage[m]['usage'] for m in mel_usage.keys()])
    unused_mel_glosses = Counter([mel_stats[m] for m in mel_stats.keys()])

    coverage_statistics.add_stat('distinct_input_glosses', len(glosses))
    # coverage_statistics.add_stat('not_matched', all_not_matched)
    # coverage_statistics.add_stat('forms', all_forms)
    coverage_statistics.add_stat('unused_mels', unused_mels[False])
    coverage_statistics.add_stat('number_of_mels', number_of_mels)
    coverage_statistics.add_stat('number_of_mels_glosses', len(mel_glosses))
    coverage_statistics.add_stat('unused_mel_glosses', unused_mel_glosses[0])
    coverage_statistics.add_stat('used_mel_glosses', len(mel_glosses) - unused_mel_glosses[0])
    # coverage_statistics.add_stat('mel_glosses', mel_glosses)

    coverage_statistics.unmatched_by_language = glosses_not_matched_by_language
    coverage_statistics.unmatched_glosses = unmatched_glosses
    coverage_statistics.matched_glosses = matched_glosses
    coverage_statistics.mel_stats = mel_stats
    coverage_statistics.mel_usage = mel_usage

    print(f'\nmel summary: mels {number_of_mels}, mel glosses {len(mel_glosses)}, unused mel glosses {unused_mel_glosses[0]}, unused mels {unused_mels[False]}')
    print(f'gloss summary: {all_matched + all_not_matched} distinct glosses, {all_matched} matched, {all_not_matched} did not match, {all_forms} forms')
    # for language in glosses_not_matched_by_language:
    #
    #     if len(glosses_not_matched_by_language[language]) > 0:
    #         print(language)
    #         print(glosses_not_matched_by_language[language])

    return coverage_statistics

def check_glosses(settings, args, glosses):
    x = settings
    g = glosses
    pass