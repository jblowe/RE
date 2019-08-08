import read
import RE
import os
import sys
import time
import coverage
import compare
import load_hooks
import utils
import serialize
import projects
import shutil
from argparser import command_args, args

print(time.asctime())
print('Command line options used: ' + ' '.join(sys.argv[1:]))

if command_args.command == 'coverage':
    print(f'checking {args.project} glosses in {args.mel_name} mel:')
    parameters_file = os.path.join(args.experiment_path,
                                   f'{args.project}.master.parameters.xml')
    settings = read.read_settings_file(parameters_file,
                                       mel=args.mel_name)
    coverage_statistics = coverage.check_mel_coverage(settings)
    coverage_xml_file = os.path.join(args.experiment_path,
                                     f'{args.project}.{args.mel_name}.coverage.statistics.xml')
    args.run = args.mel_name
    RE.write_xml_stats(coverage_statistics, settings, args, coverage_xml_file)
elif command_args.command == 'new-experiment':
    shutil.copytree(
        os.path.join('..', 'projects', args.project),
        os.path.join('..', 'experiments', args.project, args.experiment_name))
    print('created new experiment')
elif command_args.command == 'compare' or command_args.command == 'diff':
    both = f'{args.run1}+{args.run2}'
    parameters_file = os.path.join(args.experiment_path1,
                                   f'{args.project}.master.parameters.xml')
    settings = read.read_settings_file(parameters_file)
    # HACK we need this to fuzzy things correctly if we have TGTM
    if args.project == 'TGTM':
        load_hooks.load_hook(args.experiment_path1, settings)
    attested_lexicons = read.read_attested_lexicons(settings)
    B1 = read.read_proto_lexicon(
        os.path.join(args.experiment_path1,
                     f'{args.project}.{args.run1}.sets.json'))
    B2 = read.read_proto_lexicon(
        os.path.join(args.experiment_path2,
                     f'{args.project}.{args.run2}.sets.json'))
    RE.compare_isomorphic_proto_lexicons(B1, B2, attested_lexicons, command_args.command)

    # analysis_file = os.path.join(args.experiment_path1, f'{args.project}.{both}.analysis.txt')
    evaluation_stats = RE.compare_proto_lexicons(B1, B2)
    evaluation_stats['sets_1'] = (f'{args.experiment1}: {args.project}.{args.run1}', 'string')
    evaluation_stats['sets_2'] = (f'{args.experiment2}: {args.project}.{args.run2}', 'string')
    evaluation_xml_file = os.path.join(args.experiment_path1, f'{args.project}.{both}.evaluation.statistics.xml')
    RE.write_evaluation_stats(evaluation_stats, evaluation_xml_file)

    # make comparisons if there are things to compare
    for what_to_compare in 'upstream evaluation mel'.split(' '):
        compare.compare(args.experiment_path1, args.project, what_to_compare)
elif command_args.command == 'upstream':
    parameters_file = os.path.join(args.experiment_path,
                                   f'{args.project}.master.parameters.xml')
    settings = read.read_settings_file(parameters_file,
                                       mel=args.mel,
                                       fuzzy=args.fuzzy,
                                       recon=args.recon)
    load_hooks.load_hook(args.experiment_path, settings)
    # HACK: The statement above and the statement below are no longer
    # independent due to fuzzying in TGTM...
    attested_lexicons = read.read_attested_lexicons(settings)

    B = RE.batch_all_upstream(settings, attested_lexicons=attested_lexicons, only_with_mel=args.only_with_mel)
    if True:
        keys_file = os.path.join(args.experiment_path, f'{args.project}.{args.run}.keys.csv')
        RE.dump_keys(B, keys_file)
        print(f'wrote {len(B.statistics.keys)} keys and {len(B.statistics.failed_parses)} failures to {keys_file}')
        sets_file = os.path.join(args.experiment_path, f'{args.project}.{args.run}.sets.txt')
        RE.dump_sets(B, sets_file)
        print(f'wrote {len(B.forms)} text sets to {sets_file}')
        sets_xml_file = os.path.join(args.experiment_path, f'{args.project}.{args.run}.sets.xml')
        RE.dump_xml_sets(B, sets_xml_file)
        print(f'wrote {len(B.forms)} xml sets to {sets_xml_file}')
        # failures (no parses)
        failures_xml_file = os.path.join(args.experiment_path, f'{args.project}.{args.run}.failures.sets.xml')
        RE.dump_xml_sets(RE.Lexicon(B.language, [
            RE.ProtoForm('failed', (), sorted(B.statistics.failed_parses, key=lambda x: x.language)[:2000],
                         (), [])],
                         B.statistics), failures_xml_file)
        print(f'wrote {len(B.statistics.failed_parses)} failures to {failures_xml_file}')
        for c in sorted(B.statistics.correspondences_used_in_recons, key= lambda corr: utils.tryconvert(corr.id, int)):
            if c in B.statistics.correspondences_used_in_sets:
                set_count = B.statistics.correspondences_used_in_sets[c]
            else:
                set_count = 0
            # print(f'{c}', '%s %s' % (B.statistics.correspondences_used_in_recons[c], set_count))
        print(f'{len(B.statistics.correspondences_used_in_recons)} correspondences used')
        # isolates
        isolates_xml_file = os.path.join(args.experiment_path, f'{args.project}.{args.run}.isolates.sets.xml')
        C, forms_used = RE.extract_isolates(B)
        C.statistics.sets = B.forms
        RE.dump_xml_sets(C, isolates_xml_file)
        C.statistics.add_stat('isolates', len(C.forms))
        C.statistics.add_stat('sets', len(B.forms))
        C.statistics.add_stat('reflexes_in_sets', len(forms_used))
        print(f'{len(forms_used)} different reflexes in cognate sets')
        print(f'wrote {len(C.forms)} isolates to {isolates_xml_file}')
        stats_xml_file = os.path.join(args.experiment_path, f'{args.project}.{args.run}.upstream.statistics.xml')
        RE.write_xml_stats(C.statistics, settings, args, stats_xml_file)
        print('serializing proto_lexicon')
        serialize.serialize_proto_lexicon(
            B,
            os.path.join(args.experiment_path,
                         f'{args.project}.{args.run}.sets.json'))
    # make comparisons if there are things to compare
    for what_to_compare in 'upstream evaluation mel'.split(' '):
        compare.compare(args.experiment_path, args.project, what_to_compare)
else:
    print(f'unknown command {command_args.command}')
print(time.asctime())
