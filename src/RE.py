import itertools
import read
import regex as re
import os
import sys
import serialize
import collections
import mel
from copy import copy, deepcopy

class Debug:
    debug = False

class SyllableCanon:
    def __init__(self, sound_classes, syllable_regex, supra_segmentals, context_match_type):
        self.sound_classes = sound_classes
        self.regex = re.compile(syllable_regex)
        self.supra_segmentals = supra_segmentals
        self.context_match_type = context_match_type

class Correspondence:
    def __init__(self, id, context, syllable_types, proto_form, daughter_forms):
        self.id = id
        # context is a tuple of left and right contexts
        self.context = context
        self.syllable_types = syllable_types
        self.proto_form = proto_form
        # daughter forms indexed by language
        self.daughter_forms = daughter_forms

    def __repr__(self):
        return f'<Correspondence({self.id}, {self.syllable_types}, {self.proto_form})>'
        #return f'{self.id}, {",".join(self.syllable_types)}, {self.proto_form}'

# A rule is like a correspondence that only applies to a subset of
# languages. Absence of a rule implies nothing changes. There is also
# chronology with rules, as they can be applied in stages until we
# reach a 'stage 0' form which is then used to compare with other
# daughter languages via Correspondences. Thus, rules can almost be
# viewed as staged "synchronic" phonology. We ignore syllable types
# for now since we don't have a reprsentation for a syllable canon at
# each stage,
class Rule:
    def __init__(self, id, context, input, outcome, languages, stage):
        self.id = id
        # context is a tuple of left and right contexts
        self.context = context
        self.input = input
        self.outcome = outcome
        self.languages = languages
        self.stage = stage

    def __repr__(self):
        return f'<Rule({self.id}, {self.input}, {self.outcome}, {self.languages}, {self.stage})>'

class Lexicon:
    def __init__(self, language, forms, statistics=None):
        self.language = language
        self.forms = forms
        self.statistics = statistics

    def key_forms_by_glyphs_and_gloss(self):
        return {(form.glyphs, form.gloss): form for form in self.forms}

def correspondences_as_proto_form_string(cs):
    return ''.join(c.proto_form for c in cs)

def correspondences_as_ids(cs):
    return ' '.join('%4s' % c.id for c in cs)

def syllable_structure(cs):
    return ''.join(pretty_join(c.syllable_types) for c in cs)

def pretty_join(c):
    if len(c) > 1:
        return f'({",".join(c)})'
    else:
        return c[0]

def context_as_string(context):
    return ('' if context == (None, None) else
            ','.join(context[0] or '') + '_'
            + ','.join(context[1] or ''))

def read_context_from_string(string):
    return ((None, None) if string == '' else
            tuple(None if x == '' else
                  [y.strip() for y in x.split(',')]
                  for x in string.split('_')))

# build a map from tokens to lists of correspondences containing the
# token key.
# also return all possible token lengths
def partition_correspondences(correspondences, accessor):
    partitions = collections.defaultdict(list)
    for c in correspondences:
        for token in accessor(c):
            partitions[token].append(c)
    return partitions, list(set.union(*(set(map(len, accessor(c)))
                                        for c in correspondences)))

# imperative interface
class TableOfCorrespondences:
    initial_marker = Correspondence('', (None, None), '', '$', [])

    def __init__(self, family_name, daughter_languages):
        self.correspondences = []
        self.rules = []
        self.family_name = family_name
        self.daughter_languages = daughter_languages

    def add_correspondence(self, correspondence):
        self.correspondences.append(correspondence)

    def add_rule(self, rule):
        self.rules.append(rule)

    def rule_view(self):
        # make a rule view of the form
        # |Rule|Type|*|Outcome|Context|Language(s)
        partitions, lengths = partition_correspondences(self.correspondences,
                                                        lambda c: c.proto_form)

        def outcomes(c):
            outcomes = collections.defaultdict(list)
            for lang, forms in c.daughter_forms.items():
                for form in forms:
                    outcomes[form].append(lang)
            return outcomes

        return [[c.id, c.syllable_types, c.proto_form,
                 outcome, c.context, langs]
                for token, cs in partitions.items()
                for c in cs
                for outcome, langs in outcomes(c).items()]

class Parameters:
    def __init__(self, table, syllable_canon, proto_language_name, mels):
        self.table = table
        self.syllable_canon = syllable_canon
        self.proto_language_name = proto_language_name
        self.mels = mels

    def serialize(self, filename):
        serialize.serialize_correspondence_file(filename, self)

class Form:
    def __init__(self, language, glyphs):
        self.language = language
        self.glyphs = glyphs

    def __str__(self):
        return f'{self.language} {self.glyphs}'

class ModernForm(Form):
    def __init__(self, language, glyphs, gloss, id):
        super().__init__(language, glyphs)
        self.gloss = gloss
        self.id = id

    def __str__(self):
        return f'{super().__str__()}\t{self.gloss}\t{self.id}'

class Stage0Form(Form):
    def __init__(self, form, history):
        glyphs = history[0][0]
        super().__init__('proto-' + form.language, glyphs)
        self.modern = form
        self.gloss = form.gloss
        self.history = history
        self.attested_support = frozenset([form])

    def __str__(self):
        return f'{self.language} *{self.glyphs}'

class ProtoForm(Form):
    def __init__(self, language, correspondences, supporting_forms,
                 attested_support, mel):
        super().__init__(language,
                         correspondences_as_proto_form_string(
                             correspondences))
        self.correspondences = correspondences
        self.supporting_forms = supporting_forms
        self.attested_support = attested_support
        self.mel = mel

    def __str__(self):
        return f'{self.language} *{self.glyphs} = {correspondences_as_ids(self.correspondences)} {syllable_structure(self.correspondences)}'

class ProjectSettings:
    def __init__(self, directory_path, mel_filename, attested, proto_languages,
                 target, upstream, downstream, other):
        self.mel_filename = (os.path.join(directory_path,
                                          mel_filename)
                             if mel_filename else None)
        self.directory_path = directory_path
        self.attested = attested
        self.proto_languages = proto_languages
        self.upstream_target = target
        self.upstream = upstream
        self.downstream = downstream
        self.other = other

class Statistics:
    def __init__(self):
        self.failed_parses = set()
        self.singleton_support = set()
        self.summary_stats = {}
        self.language_stats = {}
        self.correspondences_used_in_recons = collections.Counter()
        self.correspondences_used_in_sets = collections.Counter()
        self.notes = []
        self.debug_notes = []

    def add_note(self, note):
        print(note)
        self.notes.append(note)

    def add_stat(self, stat, value):
        self.summary_stats[stat] = value

    def add_debug_note(self, note):
        # print(note)
        self.debug_notes.append(note)

def expanded_contexts(rule, i, sound_classes):
    contexts = set()
    if rule.context[i] is None:
        return None
    for context in rule.context[i]:
        if context in sound_classes:
            contexts.update(sound_classes[context])
        else:
            contexts.add(context)
    return contexts

# statically compute which correspondences can actually follow from
# others based on context
def next_correspondence_map(parameters):
    regex = parameters.syllable_canon.regex
    sound_classes = parameters.syllable_canon.sound_classes
    correspondences = parameters.table.correspondences
    supra_segmentals = parameters.syllable_canon.supra_segmentals
    context_match_type = parameters.syllable_canon.context_match_type

    # expand out the cover class abbreviations
    for correspondence in correspondences:
        correspondence.expanded_context = (
            expanded_contexts(correspondence, 0, sound_classes),
            expanded_contexts(correspondence, 1, sound_classes))

    def matches_this_left_context(c, last):
        return (c.context[0] is None or
                (any(last.proto_form.startswith(context)
                     for context in c.expanded_context[0])
                 if context_match_type == 'glyphs' else
                 last.proto_form in c.expanded_context[0]))

    def matches_last_right_context(c, last):
        # implements bypassing of suprasegmentals the other way
        if c.proto_form in supra_segmentals:
            return True
        return (last.context[1] is None or
                (any(c.proto_form.startswith(context)
                     for context in last.expanded_context[1])
                 if context_match_type == 'glyphs' else
                 c.proto_form in last.expanded_context[1]))

    def matches_context(c, last):
        return (matches_this_left_context(c, last) and
                matches_last_right_context(c, last))

    next_map = collections.defaultdict(set)
    for c in [parameters.table.initial_marker] + correspondences:
        for nextc in correspondences:
            if matches_context(nextc, c):
                next_map[c].add(nextc)
    return next_map

# build a map from tokens to lists of rules containing the token key.
# also return all possible token lengths
def partition_rules(rules, language):
    partitions = collections.defaultdict(list)
    token_lengths = []
    max_stage = 1
    for rule in rules:
        if language in rule.languages:
            if rule.stage < 1:
                raise Exception('Stage must be greater than or equal to 1')
            partitions[rule.outcome].append(rule)
            token_lengths.append(len(rule.outcome))
            max_stage = max(max_stage, rule.stage)
    return partitions, token_lengths, max_stage

# This class represents the state of yet-to-be-matched-and-consumed
# portions of right contexts during rule parsing, which people use to
# check that a potential parse is valid. This is a functional data
# structure which returns new instances rather than mutates itself.
#
# XXXXX Not 100% debugged yet especially with long segments or
# multiple outstanding contexts.
class RContextQueue:
    def __init__(self, todo):
        # todo is a list of lists (contexts which are valid)
        self.todo = todo

    # Add the expanded contexts for rule to self, returning a new
    # instance.
    def add_rule_right_contexts(self, rule):
        if rule.context[1] == None:
            return self
        return RContextQueue([rule.expanded_context[1]] + self.todo)

    # If segment matches every context group in self, consume the
    # segment in each matching context in the context group, returning
    # a new instance. Otherwise return false.
    def match_consume(self, segment):
        new = []
        for contexts in self.todo:
            new_group = []
            matches = True
            for context in contexts:
                if segment.startswith(context):
                    pass
                elif context.startswith(segment):
                    new_group.append(context[len(segment):])
                else:
                    matches = False
            if matches is False:
                return False
            if new_group:
                new.append(new_group)
        return RContextQueue(new)

    # We are in the 'end' state if there are no outstanding contexts
    # or the only group left has an end of parse marker '#'.
    def end(self):
        for contexts in self.todo:
            ok = False
            for context in contexts:
                if context == '#':
                    ok = True
            if ok is False:
                return False
        return True

# create a rule applier that applies rules to yield stage 0
# forms. unlike for tokenizing we don't generate all possibilities;
# because we don't have a separate syllable canon there are not really
# multiple analysis to try, and hence we just scan the form at each
# stage and perform string substitution to get the form at a previous
# stage.
def make_apply_rules(parameters, language):
    rules = parameters.table.rules
    sound_classes = parameters.syllable_canon.sound_classes
    rule_map, token_lengths, max_stage = partition_rules(rules, language)

    # expand out the cover class abbreviations
    for rule in rules:
        rule.expanded_context = (
            expanded_contexts(rule, 0, sound_classes),
            expanded_contexts(rule, 1, sound_classes))

    def matches_this_left_context(rule, input):
        return (rule.context[0] is None or
                any(input.endswith(context) if context != '$'
                    else input == ''
                    for context in rule.expanded_context[0]))

    def apply_rules(form):
        # for each stage, generate the candidate forms for the next
        # stage.
        candidates = [(form, [])]
        next_candidates = []
        for stage in reversed(range(max_stage + 1)):
            def gen_next_candidates(form, history):
                # consume tokens from outcome, applying all possible
                # applicable rules to build input, and also generate a
                # form where nothing changed.
                def gen(outcome, input, rqueue, applied_rules):
                    if outcome == '':
                        if rqueue.end():
                            next_candidates.append((input,
                                                    [(input, applied_rules)] + history
                                                    if applied_rules != []
                                                    else history))
                        return
                    for token_length in token_lengths:
                        for rule in rule_map[outcome[:token_length]]:
                            if rule.stage == stage:
                                rmatch = rqueue.match_consume(rule.input)
                                if (rmatch
                                    and matches_this_left_context(rule, input)):
                                    gen(outcome[token_length:],
                                        input + rule.input,
                                        rmatch.add_rule_right_contexts(rule),
                                        applied_rules + [rule])
                    rmatch = rqueue.match_consume(outcome[0])
                    if rmatch:
                        gen(outcome[1:], input + outcome[0], rmatch, applied_rules)
                gen(form, '', RContextQueue([]), [])
            for (candidate, history) in candidates:
                gen_next_candidates(candidate, history)
            candidates = next_candidates
            next_candidates = []
        return candidates

    return apply_rules

# tokenize an input string and return the set of all parses
# which also conform to the syllable canon
def make_tokenizer(parameters, accessor, next_map):
    regex = parameters.syllable_canon.regex
    sound_classes = parameters.syllable_canon.sound_classes
    supra_segmentals = parameters.syllable_canon.supra_segmentals
    correspondences = parameters.table.correspondences
    rule_map, token_lengths = partition_correspondences(
        correspondences,
        accessor)

    def tokenize(form, statistics):
        parses = set()
        attempts = set()

        def gen(form, parse, last, syllable_parse):
            '''We generate context and "phonotactic" sensitive parses recursively,
            making sure to skip over suprasegmental features when matching
            contexts.
            '''
            # we can abandon parses that we know can't be completed
            # to satisfy the syllable canon. for DEMO93 this cuts the
            # number of branches from 182146 to 61631
            match = regex.fullmatch(syllable_parse, partial=True)
            if match is None:
                if Debug.debug:
                    pass
                    #filler = '. ' * len(parse)
                    #statistics.add_debug_note(f'{filler}canon cannot match: {len(parse)}, {form}, *{correspondences_as_proto_form_string(parse)}, {correspondences_as_ids(parse)}, {syllable_parse}')
                return
            if Debug.debug:
                pass
                #filler = '. ' * len(parse)
                #statistics.add_debug_note(f'{filler}{len(parse)}, {form}, *{correspondences_as_proto_form_string(parse)}, {correspondences_as_ids(parse)}, {syllable_parse}')
            if form == '':
                # check whether the last token's right context had a word final
                # marker or a catch all environment
                if (last.context[1] is None or
                        '#' in last.expanded_context[1]):
                    if match.partial is False:
                        parses.add(tuple(parse))
                    attempts.add(tuple(parse))
            # if the last token was marked as only word final then stop
            if last.context[1] and last.expanded_context[1] == {'#'}:
                return
            # otherwise keep building parses from epenthesis rules
            for c in rule_map['∅']:
                if c in next_map[last]:
                    for syllable_type in c.syllable_types:
                        gen(form,
                            parse + [c],
                            last if c.proto_form in supra_segmentals else c,
                            syllable_parse + syllable_type)
            if form == '':
                #if Debug.debug:
                #    statistics.add_debug_note(f'reached end of form!')
                return
            for token_length in token_lengths:
                for c in rule_map[form[:token_length]]:
                    if c in next_map[last]:
                        for syllable_type in c.syllable_types:
                            gen(form[token_length:],
                                parse + [c],
                                last if c.proto_form in supra_segmentals else c,
                                syllable_parse + syllable_type)

        gen(form, [], parameters.table.initial_marker, '')
        if Debug.debug:
            statistics.add_debug_note(f'{len(parses)} reconstructions generated')
            for p in attempts:
                if p in parses:
                    statistics.add_debug_note(f' *{correspondences_as_proto_form_string(p)} - {correspondences_as_ids(p)} {syllable_structure(p)}')
                else:
                    statistics.add_debug_note(f' xx {correspondences_as_proto_form_string(p)} - {correspondences_as_ids(p)} {syllable_structure(p)}')
        return parses
    return tokenize

# set of all possible forms for a daughter language given correspondences
def postdict_forms_for_daughter(correspondences, daughter):
    return frozenset(''.join(token) for token in
                     itertools.product(*[c.daughter_forms[daughter]
                                         for c in correspondences]))

# return a mapping from daughter language to all possible forms given a proto-form
def postdict_daughter_forms(proto_form, parameters):
    postdict = {}  # pun?
    # big speed difference between [c.proto_form] vs c.proto_form
    # c.proto_form does lots of slow substring comparisons. [c.proto_form]
    # parallels the usage of the other daughter form accessors
    tokenize = make_tokenizer(parameters, lambda c: [c.proto_form])
    for cs in iter(tokenize(proto_form)):
        for language in parameters.table.daughter_languages:
            postdict[language] = postdict_forms_for_daughter(cs, language)
    return postdict

# return a mapping from reconstructions to its supporting forms
def project_back(lexicons, parameters, statistics):
    reconstructions = collections.defaultdict(list)
    next_map = next_correspondence_map(parameters)
    number_of_forms = 0
    for lexicon in lexicons:
        # we don't want to tokenize the same glyphs more than once, so
        # memoize each parse
        memo = {}
        daughter_form = lambda c: c.daughter_forms[lexicon.language]
        count_of_parses = 0
        count_of_no_parses = 0
        tokenize = make_tokenizer(parameters, daughter_form, next_map)
        apply_rules = make_apply_rules(parameters, lexicon.language)
        for form in lexicon.forms:
            if form.glyphs == '':
                continue
            statistics.add_debug_note(f'!Parsing {form}...')
            if form.glyphs:
                def all_tokenizations():
                    parses = []
                    for (stage_0_form, history) in apply_rules(form.glyphs):
                        parses += [(x, history) for x in tokenize(stage_0_form, statistics)]
                    return parses
                parses = memo.setdefault(form.glyphs, all_tokenizations())
            else:
                statistics.add_note(f'form missing: {form.language} {form.gloss}')
                parses = None
            if parses:
                for (cs, history) in parses:
                    count_of_parses += 1
                    if history == []:
                        reconstructions[cs].append(form)
                    else:
                        proto_stage_0_form = Stage0Form(form, history)
                        reconstructions[cs].append(proto_stage_0_form)
            else:
                count_of_no_parses += 1
                statistics.failed_parses.add(form)
        number_of_forms += len(lexicon.forms)
        statistics.language_stats[lexicon.language] = {'forms': len(lexicon.forms), 'no_parses': count_of_no_parses, 'reconstructions': count_of_parses}
        statistics.add_note(f'{lexicon.language}: {len(lexicon.forms)} forms, {count_of_no_parses} no parses, {count_of_parses} reconstructions')
    statistics.correspondences_used_in_recons = count_correspondences_used_in_reconstructions(reconstructions)
    statistics.add_stat('lexicons', len(lexicons))
    statistics.add_stat('reflexes', number_of_forms)
    statistics.add_note(f'{number_of_forms} input forms')
    statistics.keys = reconstructions
    return reconstructions, statistics

def count_correspondences_used_in_reconstructions(reconstructions):
    correspondences_used = collections.Counter()
    for r in reconstructions:
        correspondences_used.update([correspondence for correspondence in r])
    return correspondences_used

def count_correspondences_used_in_sets(cognate_sets):
    correspondences_used = collections.Counter()
    for c in cognate_sets:
        correspondences_used.update([correspondence for correspondence in c[0]])
    return correspondences_used

# we create cognate sets by comparing meaning.
def create_sets(projections, statistics, mels, only_with_mel, root=True):
    cognate_sets = set()

    def attested_forms(support):
        attested = set()
        for x in support:
            if isinstance(x, ModernForm):
                attested.add(x)
            else:
                attested |= x.attested_support
        return attested

    def all_glosses(projections):
        all_glosses = set()
        for support in projections.values():
            for supporting_form in support:
                if isinstance(supporting_form, ModernForm):
                    if supporting_form.gloss:
                        all_glosses.add(supporting_form.gloss)
        return all_glosses

    associated_mels_table = mel.compile_associated_mels(mels,
                                                        all_glosses(projections))

    def add_cognate_sets(reconstruction, support):
        distinct_mels = collections.defaultdict(list)
        for supporting_form in support:
            if isinstance(supporting_form, ModernForm):
                for associated_mel in mel.associated_mels(associated_mels_table,
                                                          supporting_form.gloss):
                    if not (only_with_mel and associated_mel.id == '') or mels is None:
                        distinct_mels[associated_mel].append(supporting_form)
            else:
                distinct_mels[mel.default_mel].append(supporting_form)
        for distinct_mel, support in distinct_mels.items():
            if not root or len({form.language for form in support}) > 1:
                cognate_sets.add((reconstruction,
                                  frozenset(support),
                                  frozenset(attested_forms(support)),
                                  distinct_mel))
            else:
                statistics.singleton_support.add((reconstruction,
                                                  frozenset(support),
                                                  frozenset(attested_forms(support)),
                                                  distinct_mel))

    for reconstruction, support in projections.items():
        add_cognate_sets(reconstruction, support)
    statistics.add_note(
        f'{len(cognate_sets)} sets supported by multiple languages'
        if root else
        f'{len(cognate_sets)} cognate sets')
    statistics.correspondences_used_in_sets = count_correspondences_used_in_sets(cognate_sets)
    return cognate_sets, statistics

# given a collection of sets, we want to find all maximal sets,
# i.e. ones which are not proper subsets of any other set in the
# collection. we do this by partitioning the collection of sets by
# each set's length to reduce unnecessary comparison
def filter_subsets(cognate_sets, statistics, root=True):
    partitions = collections.defaultdict(list)
    index = 2 if root else 1
    support_class = collections.defaultdict(list)
    # collect all sets with the same support. if one loses, they all lose.
    for cognate_set in cognate_sets:
        support_class[cognate_set[index]].append(cognate_set)
    for support in support_class.keys():
        partitions[len(support)].append(support)
    losers = set()
    # the largest sets are never losers
    for key1, sets1 in sorted(partitions.items(), reverse=True)[1:]:
        larger_sets = [set for key2, sets2 in partitions.items()
                       if key2 > key1
                       for set in sets2
                       if support_class[set][0] not in losers]
        for support_set in sets1:
            for support_set2 in larger_sets:
                if support_set < support_set2:
                    for cognate_set in support_class[support_set]:
                        losers.add(cognate_set)
                    break
    statistics.subsets = losers
    statistics.add_note(f'threw away {len(losers)} subsets')
    statistics.add_stat('subsets_tossed', len(losers))
    return cognate_sets - losers, statistics

# pick a representative derivation, i.e. choose a reconstruction from
# reconstructions with the same supporting forms yielding the same
# surface string
def pick_derivation(cognate_sets, statistics, only_with_mel):
    uniques = {}
    for cognate_set in cognate_sets:
        uniques[(correspondences_as_proto_form_string(cognate_set[0]), cognate_set[1])] = cognate_set
    statistics.add_note(f'{len(uniques)} distinct reconstructions with distinct supporting forms')
    reflexes = sum([len(x[1]) for x in list(uniques.values())])
    statistics.add_note(f'{reflexes} reflexes in sets')
    statistics.add_stat('reflexes_in_sets', reflexes)
    return uniques.values(), statistics

def batch_upstream(lexicons, params, only_with_mel, root):
    return pick_derivation(
        *filter_subsets(
            *create_sets(
                *project_back(lexicons, params, Statistics()),
                params.mels,
                only_with_mel,
                root),
            root),
            only_with_mel)

def upstream_tree(target, tree, param_tree, attested_lexicons, only_with_mel):
    # batch upstream repeatedly up the action graph tree from leaves,
    # which are necessarily attested. we filter forms with singleton
    # supporting sets for the root language
    def rec(target, root):
        if target in attested_lexicons:
            return attested_lexicons[target]
        daughter_lexicons = [rec(daughter, False)
                             for daughter in tree[target]]
        forms, statistics = batch_upstream(daughter_lexicons,
                                           param_tree[target],
                                           only_with_mel,
                                           root)
        return Lexicon(
            target,
            [ProtoForm(target, correspondences, supporting_forms,
                       attested_support, mel)
             for (correspondences, supporting_forms, attested_support, mel)
             in forms],
            statistics)

    return rec(target, True)

def all_parameters(settings):
    # Return a mapping from protolanguage to its associated parameter object
    mapping = {}

    def rec(target):
        if target in settings.attested:
            return
        mapping[target] = \
            read.read_correspondence_file(
                os.path.join(settings.directory_path,
                             settings.proto_languages[target]),
                '------',
                list(settings.upstream[target]),
                target,
                settings.mel_filename)
        for daughter in settings.upstream[target]:
            rec(daughter)

    rec(settings.upstream_target)
    return mapping

def batch_all_upstream(settings, only_with_mel=False):
    attested_lexicons = read.read_attested_lexicons(settings)
    return upstream_tree(settings.upstream_target,
                         settings.upstream,
                         all_parameters(settings),
                         attested_lexicons,
                         only_with_mel)

def interactive_upstream(settings, attested_lexicons, only_with_mel=False):
    # attested_lexicons are passed in for this type of upstream...
    return upstream_tree(settings.upstream_target,
                         settings.upstream,
                         all_parameters(settings),
                         attested_lexicons,
                         only_with_mel)

def print_form(form, level):
    if isinstance(form, ModernForm):
        print('  ' * level + str(form))
    elif isinstance(form, ProtoForm):
        print('  ' * level + str(form) + ' ' +
              correspondences_as_ids(form.correspondences))
        # TODO: the output order should be the 'preferred order', not just alphabetical. but how?
        for supporting_form in sorted(form.supporting_forms, key=lambda x: x.language + x.glyphs):
            print_form(supporting_form, level + 1)
    elif isinstance(form, Stage0Form):
        print(" TODO don't know how to display Stage0FOrm yet ")

def print_sets(lexicon):
    # for form in lexicon.forms:
    for form in sorted(lexicon.forms, key=lambda corrs: correspondences_as_ids(corrs.correspondences)):
        print_form(form, 0)

def dump_sets(lexicon, filename):
    out = sys.stdout
    with open(filename, 'w', encoding='utf-8') as sys.stdout:
        print_sets(lexicon)
    sys.stdout = out

def dump_xml_sets(sets, languages, filename, only_with_mel):
    serialize.serialize_sets(sets, languages, filename, only_with_mel)

def dump_keys(lexicon, filename):
    out = sys.stdout
    forms = []
    with open(filename, 'w', encoding='utf-8') as sys.stdout:
        for reconstruction, support in lexicon.statistics.keys.items():
            for support1 in support:
                forms.append(str(support1) + f'\t*{correspondences_as_proto_form_string(reconstruction)}\t*{correspondences_as_ids(reconstruction)}')
        print('\t'.join('language & form,gloss,id,protoform,correspondences'.split(',')))
        for i,f in enumerate(sorted(forms)):
            if i > 100000:
                print('**** output terminated after 100,000 lines')
                break
            print(f)
        print('***failures')
        for failure in lexicon.statistics.failed_parses:
            print(f'{str(failure)}')
    sys.stdout = out

def compare_support(lex1_forms, forms):
    # FIXME: there's a subtle dependency here on the Form.str method.
    return sorted([str(k) for k in lex1_forms]) == sorted([str(k) for k in forms])

def set_compare(lex1, lex2, languages):
    union = lex1 + lex2
    list_of_sf = collections.defaultdict(list)
    overlap = collections.defaultdict(list)
    for i in union:
        # print(i)
        for j in i.supporting_forms:
            # print(f'   {j}')
            if not i in list_of_sf[j]:
                list_of_sf[j].append(i)

    graph = collections.defaultdict(list)
    pfms = set()
    for i, form in enumerate(list_of_sf):
        sets = list_of_sf[form]
        for protoform in sets:
            pformshort = f'{protoform.glyphs} {correspondences_as_ids(protoform.correspondences)}'
            try:
                reflexshort = f'{form.language} {form.glyphs} {form.gloss}'
            except:
                reflexshort = f'{form.language} {form.glyphs} {i}'
            pfms.add(pformshort)
            if not pformshort in graph[reflexshort]:
                graph[reflexshort].append(pformshort)

    pfms = list(pfms)
    refs = list(graph.keys())

    return list_of_sf, graph, pfms, refs



def make_set(l1,l2,diff, union):
    MF = []
    for s in sorted(diff):
        for x in diff[s]:
            m = deepcopy(union[x])
            m.membership = s
            MF.append(m)
    # ProtoForm(lexicon.language, correspondences, supporting_forms, attested_support, mel)
    return ProtoForm(l1.language,
              l1.correspondences,
              MF,
              MF,
              l1.mel
              )

def compare_proto_lexicons(lexicon1, lexicon2, languages):
    table = collections.defaultdict(list)
    common = set()
    only_lex2 = set()
    for form in lexicon1.forms:
        table[form.glyphs].append(form)
    for form in lexicon2.forms:
        if table[form.glyphs] == []:
            only_lex2.add(form)
        else:
            lex1_forms = table[form.glyphs]
            form_matched = False
            for lex1_form in lex1_forms:
                if compare_support(lex1_form.supporting_forms, form.supporting_forms):
                    common.add(lex1_form)
                    form_matched = True
            if not form_matched:
                only_lex2.add(form)
    only_lex1 = set(lexicon1.forms).difference(common)
    ncommon = len(common)
    nl1 = len(lexicon1.forms)
    nl2 = len(lexicon2.forms)
    precision = ncommon / nl1
    recall = ncommon / nl2
    fscore = 2 * (precision * recall) / (precision + recall)
    # TODO: is it useful to simply print these stats. Ever?
    print(f'Number of sets in lexicon 1: {nl1}')
    print(f'Number of sets in lexicon 2: {nl2}')
    print(f'Number of sets in common: {ncommon}')
    print(f'Number of sets only in lexicon 1: {len(only_lex1)}')
    print(f'Number of sets only in lexicon 2: {len(only_lex2)}')
    print('Assuming set 1 is gold:')
    print(f'  Precision: {precision}')
    print(f'  Recall: {recall}')
    print(f'  F-score: {fscore}')
    # TODO: leave in for now, but figure out how to render the diff better..
    # print(f'Sets only in lexicon1:')
    # for form in only_lex1:
    #     print_form(form, 0)
    # print(f'Sets only in lexicon2:')
    # for form in only_lex2:
    #     print_form(form, 0)
    # print('Sets in common:')
    # for form in common:
    #     print_form(form, 0)
    list_of_sf, graph, pfms, refs = set_compare(list(only_lex1), list(only_lex2), languages)

    return {
        'number_of_sets_in_lexicon_1': nl1,
        'number_of_sets_in_lexicon_2': nl2,
        'number_of_sets_in_common': ncommon,
        'number_of_sets_only_in_lexicon_1': len(only_lex1),
        'number_of_sets_only_in_lexicon_2': len(only_lex2),
        'venn': f'{len(only_lex1)},{len(only_lex2)},{ncommon}',
        'precision': ('{:04.3f}'.format(precision), 'float'),
        'recall': ('{:04.3f}'.format(recall), 'float'),
        'fscore': ('{:04.3f}'.format(fscore), 'float'),
        'sets_in_common': list(common),
        'sets_only_in_lexicon1': list(only_lex1),
        'sets_only_in_lexicon2': list(only_lex2),
        'list_of_sf': list_of_sf,
        'number_of_pfms': len(pfms),
        'number_of_refs': len(refs),
        'graph': graph,
        'pfms': pfms,
        'refs': refs
    }


# def compare_isomorphic_proto_lexicons(lexicon1, lexicon2, compare_type):
#     # replace_underlying_lexicons(lexicon1, attested_lexicons)
#     # replace_underlying_lexicons(lexicon2, attested_lexicons)
#     return compare_proto_lexicons(lexicon1, lexicon2)

# create a fake cognate set with the forms that failed to reconstruct
def extract_failures(lexicon):
    return Lexicon(
        lexicon.language,
        [ProtoForm('failed', (), sorted(lexicon.statistics.failed_parses, key=lambda x: x.language),
                   (), [])],
        [],
        lexicon.statistics)

# create "cognate sets" for the isolates
# (and we need to check to see that the singletons really are isolates -- not in any set)
def extract_isolates(lexicon):
    forms_used = collections.Counter()

    def is_in(item, list_of_forms):
        for form in item[1]:
            if form in list_of_forms:
                return True
        return False

    for set in lexicon.forms:
        forms_used.update([supporting_form for supporting_form in set.supporting_forms])
    isolates = [item for item in lexicon.statistics.singleton_support if not is_in(item, forms_used)]
    duplicates = {}
    new_isolates = []
    for item in isolates:
        x = next(iter(item[1]))
        if not x in duplicates:
            duplicates[x] = 1
            new_isolates.append(item)
    return [ProtoForm(lexicon.language, correspondences, supporting_forms, attested_support, mel)
            for (correspondences, supporting_forms, attested_support, mel)
            in new_isolates]

# given a proto lexicon whose underlying attested forms are drawn
# from lexicons isomorphic to attested_lexicons, destructively replace
# the in-memory Form objects with those in attested_lexicons.
# daughter_lexicons is a hash table mapping language -> Lexicon.
# only works for non-tree lexicons for now.
def replace_underlying_lexicons(proto_lexicon, attested_lexicons):
    keyed_forms = {language: lexicon.key_forms_by_glyphs_and_gloss()
                   for (language, lexicon) in attested_lexicons.items()}
    for form in proto_lexicon.forms:
        def intern(form_set):
            return frozenset((keyed_forms[form.language][(form.glyphs, form.gloss)]
                              for form in form_set))
        form.attested_support = intern(form.attested_support)
        form.supporting_forms = intern(form.supporting_forms)

# Given a lexicon of protoforms, return a mapping between cognate sets
# and possible reconstructions.
def collate_proto_lexicon(proto_lexicon):
    mapping = collections.defaultdict(list)
    for proto_form in proto_lexicon:
        mapping[proto_form.supporting_forms].append(proto_form)
    return mapping
