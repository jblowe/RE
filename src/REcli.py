import read
import RE
import os
import sys
import time
import coverage
import compare
import load_hooks
import utils
import shutil
import serialize
from argparser import command_args, args

def check_setup(command, args, settings):
    # only for checking 'upstream' setup at the moment; other setups mostly checked earlier
    errors = False
    if args.recon is None:
        print('a --recon (or -t) argument is required.')
        errors = True
    if args.run is None:
        print('a --run (or -r) argument is required.')
        errors = True
    if settings.proto_languages == {}:
        print(f'{args.recon} does not seem to exist as a possible Reconstruction.')
        errors = True
    if args.fuzzy is not None and args.fuzzy not in settings.other['fuzzies']:
        print(f'{args.fuzzy} does not seem to point to a fuzzy file.')
        errors = True
    if args.mel is not None and args.mel not in settings.other['mels']:
        print(f'{args.mel} does not seem to point to a MEL file.')
        errors = True
    if errors:
        sys.exit(1)

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
    extra_mel_xml_file = os.path.join(args.experiment_path,
                                     f'{args.project}.{args.mel_name}-extra.mel.xml')
    serialize.serialize_stats(coverage_statistics, settings, args, coverage_xml_file)
    serialize.serialize_mels(coverage_statistics.unmatched_glosses, args.mel_name, extra_mel_xml_file)
elif command_args.command == 'analyze-glosses':
    settings = read.read_settings_file(os.path.join('..', 'experiments', args.project, args.experiment, f'{args.project}.master.parameters.xml'))

    glosses = sorted(utils.all_glosses(read.read_attested_lexicons(settings)))
    gloss_analysis_statistics = coverage.check_glosses(settings, args, glosses)
    gloss_analysis_xml_file = os.path.join(args.experiment_path,
                                           f'{args.project}.{args.mel_name}.gloss_analysis.statistics.xml')
    serialize.serialize_stats(gloss_analysis_statistics, settings, args, gloss_analysis_xml_file)

elif command_args.command == 'new-experiment':
    directory = os.path.join('..', 'experiments', args.project, args.experiment_name)
    if os.path.isdir(directory):
        print(f'{directory} already exists, not (re)created')
    else:
        shutil.copytree(
            os.path.join('..', 'projects', args.project),
            os.path.join('..', 'experiments', args.project, args.experiment_name))
        print(f'created new experiment')
elif command_args.command == 'delete-experiment':
    directory = os.path.join('..', 'experiments', args.project, args.experiment_name)
    if os.path.isdir(directory):
        shutil.rmtree(directory, ignore_errors=True)
        print('deleted experiment')
    else:
        print(f'{directory} does not exist, not deleted')
elif command_args.command == 'compare' or command_args.command == 'diff':
    both = f'{args.run1}-and-{args.run2}'
    parameters_file = os.path.join(args.experiment_path1,
                                   f'{args.project}.master.parameters.xml')

    # there must be a 'standard' reconstruction element for compare to work... need languages
    settings = read.read_settings_file(parameters_file,
                                       mel=None,
                                       fuzzy=None,
                                       recon='standard')

    B1 = read.read_proto_lexicon(
        os.path.join(args.experiment_path1,
                     f'{args.project}.{args.run1}.sets.json'))
    B2 = read.read_proto_lexicon(
        os.path.join(args.experiment_path2,
                     f'{args.project}.{args.run2}.sets.json'))
    # RE.compare_isomorphic_proto_lexicons(B1, B2, command_args.command)

    # analysis_file = os.path.join(args.experiment_path1, f'{args.project}.{both}.analysis.txt')
    evaluation_stats = RE.compare_proto_lexicons(B1, B2, settings.upstream[settings.upstream_target])
    evaluation_stats['set_1'] = (f'{args.experiment1}: {args.project}.{args.run1}', 'string')
    evaluation_stats['set_2'] = (f'{args.experiment2}: {args.project}.{args.run2}', 'string')
    evaluation_xml_file = os.path.join(args.experiment_path1, f'{args.project}.{both}.evaluation.statistics.xml')
    serialize.serialize_evaluation(evaluation_stats, evaluation_xml_file, settings.upstream[settings.upstream_target])

    # make comparisons if there are things to compare
    for what_to_compare in 'upstream evaluation mel'.split(' '):
        compare.compare(args.experiment_path1, args.project, what_to_compare)
elif command_args.command == 'upstream':
    print(time.asctime())
    elapsed_time = time.time()
    print('Command line options used: ' + ' '.join(sys.argv[1:]))

    parameters_file = os.path.join(args.experiment_path,
                                   f'{args.project}.master.parameters.xml')
    settings = read.read_settings_file(parameters_file,
                                       mel=args.mel,
                                       fuzzy=args.fuzzy,
                                       recon=args.recon)
    check_setup(command_args.command, args, settings)
    load_hooks.load_hook(args.experiment_path, args, settings)
    mel_status = 'strict MELs' if args.only_with_mel else 'MELs not enforced'
    print(mel_status)
    B = RE.batch_all_upstream(settings, only_with_mel=args.only_with_mel)
    keys_file = os.path.join(args.experiment_path, f'{args.project}.{args.run}.keys.csv')
    RE.dump_keys(B, keys_file)
    print(f'wrote {len(B.statistics.keys)} keys and {len(B.statistics.failed_parses)} failures to {keys_file}')
    sets_file = os.path.join(args.experiment_path, f'{args.project}.{args.run}.sets.txt')
    RE.dump_sets(B, sets_file)
    # print(f'wrote {len(B.forms)} text sets to {sets_file}')
    correspondences_used = 0
    for reference_set in B.statistics.correspondence_index.values():
        if len(reference_set) != 0:
            correspondences_used += 1
    print(f'{correspondences_used} correspondences used')
    B.isolates = RE.extract_isolates(B)
    B.failures = RE.ProtoForm('failed', (), sorted(B.statistics.failed_parses, key=lambda x: x.language), (), [])
    sets_xml_file = os.path.join(args.experiment_path, f'{args.project}.{args.run}.sets.xml')
    RE.dump_xml_sets(B, settings.upstream[settings.upstream_target], sets_xml_file, args.only_with_mel)
    # print(f'wrote {len(B.forms)} xml sets, {len(B.failures.supporting_forms)} failures and {len(B.isolates)} isolates to {sets_xml_file}')
    B.statistics.add_stat('isolates', len(B.isolates))
    B.statistics.add_stat('sets', len(B.forms))
    B.statistics.add_stat('sankey', f'{len(B.isolates)},{len(B.failures.supporting_forms)},{B.statistics.summary_stats["reflexes"]}')
    stats_xml_file = os.path.join(args.experiment_path, f'{args.project}.{args.run}.upstream.statistics.xml')
    serialize.serialize_stats(B.statistics, settings, args, stats_xml_file)
    print('serializing proto_lexicon')
    serialize.serialize_proto_lexicon(
        B,
        os.path.join(args.experiment_path,
                     f'{args.project}.{args.run}.sets.json'))
    # make comparisons if there are things to compare
    for what_to_compare in 'upstream evaluation mel'.split(' '):
        compare.compare(args.experiment_path, args.project, what_to_compare)
    print(time.asctime())
else:
    print(f'unknown command {command_args.command}')
