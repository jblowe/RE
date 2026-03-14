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
from utils import *
from read import read_settings

def check_setup(command, args, settings):
    # only for checking 'upstream' setup at the moment; other setups mostly checked earlier
    errors = False
    if args.recon is None and args.upstream is None:
        print('a --recon (or -t) argument is required if a --upstream argument is not present.')
        errors = True
    if args.run is None:
        print('a --run (or -r) argument is required.')
        errors = True
    if args.project_path is None or args.project is None:
        print(f'could not find project. does .')
        errors = True
    if settings.proto_languages == {}:
        print(f'could not construct a reconstruction tree.')
        errors = True
    if errors:
        sys.exit(1)

if command_args.command == 'coverage':
    print(f'checking {args.project} glosses in {args.mel_name} mel:')
    recon_candidates = [fn for fn in os.listdir(args.project_path)
                        if fn.startswith(f'{args.project}.') and fn.endswith('.correspondences.xml')]
    if not recon_candidates:
        raise Exception(f"No {args.project}.*.correspondences.xml files found in {args.project_path}")
    recon_token = recon_candidates[0].split('.', 2)[1]
    settings =  read_settings(args.project_path, args.project, recon_token,
                                            mel_token=args.mel_name,
                                            fuzzy_token=None,
                                            languages=None)
    coverage_statistics = coverage.check_mel_coverage(settings)
    coverage_xml_file = os.path.join(args.project_path, f'{args.project}.{args.mel_name}.coverage.statistics.xml')
    args.run = args.mel_name
    extra_mel_xml_file = os.path.join(args.project_path, f'{args.project}.{args.mel_name}-extra.mel.xml')
    serialize.serialize_stats(coverage_statistics, settings, args, coverage_xml_file)
    serialize.serialize_mels(coverage_statistics.unmatched_glosses, args.mel_name, extra_mel_xml_file)
elif command_args.command == 'analyze-glosses':
    recon_candidates = [fn for fn in os.listdir(args.project_path)
                        if fn.startswith(f'{args.project}.') and fn.endswith('.correspondences.xml')]
    if not recon_candidates:
        raise Exception(f"No {args.project}.*.correspondences.xml files found in {args.project_path}")
    recon_token = recon_candidates[0].split('.', 2)[1]
    settings =  read_settings(args.project_path, args.project, recon_token,
                                            mel_token=None,
                                            fuzzy_token=None,
                                            languages=None)

    glosses = sorted(utils.all_glosses(read.read_attested_lexicons(settings)))
    gloss_analysis_statistics = coverage.check_glosses(settings, args, glosses)
    gloss_analysis_xml_file = os.path.join(f'{args.project}.{args.mel_name}.gloss_analysis.statistics.xml')
    serialize.serialize_stats(gloss_analysis_statistics, settings, args, gloss_analysis_xml_file)

elif command_args.command == 'new-project':
    directory = os.path.join('..', 'projects', args.project)
    if os.path.isdir(directory):
        print(f'{directory} already exists, not (re)created')
    else:
        os.mkdir(os.path.join('..', 'projects', args.project))
        print(f'created new project {args.project}')
elif command_args.command == 'delete-project':
    directory = os.path.join('..', 'projects', args.project)
    if os.path.isdir(directory):
        shutil.rmtree(directory, ignore_errors=True)
        print(f'deleted project {args.project}')
    else:
        print(f'{directory} does not exist, not deleted')
elif command_args.command == 'compare' or command_args.command == 'diff':
    both = f'{args.run1}-and-{args.run2}'
    recon_candidates = [fn for fn in os.listdir(args.project_path)
                        if fn.startswith(f'{args.project}.') and fn.endswith('.correspondences.xml')]
    if not recon_candidates:
        raise Exception(f"No {args.project}.*.correspondences.xml files found in {args.project_path}")
    if any(fn == f'{args.project}.standard.correspondences.xml' for fn in recon_candidates):
        recon_token = 'standard'
    else:
        recon_token = recon_candidates[0].split('.', 2)[1]

    settings =  read_settings(args.project_path, args.project, recon_token,
                                            mel_token=None,
                                            fuzzy_token=None,
                                            upstream=None)

    B1 = read.read_proto_lexicon(
        os.path.join(args.project_path, f'{args.project}.{args.run1}.sets.json'))
    B2 = read.read_proto_lexicon(
        os.path.join(args.project_path, f'{args.project}.{args.run2}.sets.json'))
    # RE.compare_isomorphic_proto_lexicons(B1, B2, command_args.command)

    # analysis_file = os.path.join(args.project_path1, f'{args.project}.{both}.analysis.txt')
    evaluation_stats = RE.compare_proto_lexicons(B1, B2, settings.upstream[settings.upstream_target])
    evaluation_stats['set_1'] = (f'{args.project}.{args.run1}', 'string')
    evaluation_stats['set_2'] = (f'{args.project}.{args.run2}', 'string')
    evaluation_xml_file = os.path.join(args.project_path, f'{args.project}.{both}.evaluation.statistics.xml')
    serialize.serialize_evaluation(evaluation_stats, evaluation_xml_file, settings.upstream[settings.upstream_target])

    # make comparisons if there are things to compare
    for what_to_compare in 'upstream evaluation mel'.split(' '):
        compare.compare(args.project_path, args.project, what_to_compare)
elif command_args.command == 'upstream':
    print(time.asctime())
    elapsed_time = time.time()
    print('Command line options used: ' + ' '.join(sys.argv[1:]))
    # languages = split_csv(getattr(args, 'upstream', None))
    settings = read_settings(args.project_path, args.project, args.recon,
                                            mel_token=args.mel,
                                            fuzzy_token=args.fuzzy,
                                            upstream=args.upstream)
    check_setup(command_args.command, args, settings)
    load_hooks.load_hook(args.project_path)

    mel_status = 'strict MELs' if args.only_with_mel else 'MELs not enforced'
    print(mel_status)
    B = RE.batch_all_upstream(settings, only_with_mel=args.only_with_mel)
    keys_file = os.path.join(args.project_path, f'{args.project}.{args.run}.keys.csv')
    RE.dump_keys(B, keys_file)
    print(f'wrote {len(B.statistics.keys)} keys and {len(B.statistics.failed_parses)} failures to {keys_file}')
    sets_file = os.path.join(args.project_path, f'{args.project}.{args.run}.sets.txt')
    RE.dump_sets(B, sets_file)
    # print(f'wrote {len(B.forms)} text sets to {sets_file}')
    correspondences_used = 0
    for reference_set in B.statistics.correspondence_index.values():
        if len(reference_set) != 0:
            correspondences_used += 1
    print(f'{correspondences_used} correspondences used')
    B.isolates = sorted(RE.extract_isolates(B).keys(), key=lambda x: x.language)
    B.failures = sorted(B.statistics.failed_parses, key=lambda x: x.language)
    sets_xml_file = os.path.join(args.project_path, f'{args.project}.{args.run}.sets.xml')
    RE.dump_xml_sets(B, settings.upstream[settings.upstream_target], sets_xml_file, args.only_with_mel)
    # print(f'wrote {len(B.forms)} xml sets, {len(B.failures.supporting_forms)} failures and {len(B.isolates)} isolates to {sets_xml_file}')
    B.statistics.add_stat('isolates', len(B.isolates))
    B.statistics.add_stat('failure', len(B.failures))
    B.statistics.add_stat('sets', len(B.forms))
    B.statistics.add_stat('sankey', f'{len(B.isolates)},{len(B.failures)},{B.statistics.summary_stats["reflexes"]}')
    stats_xml_file = os.path.join(args.project_path, f'{args.project}.{args.run}.upstream.statistics.xml')
    serialize.serialize_stats(B.statistics, settings, args, stats_xml_file)
    # make comparisons if there are things to compare
    # for what_to_compare in 'upstream evaluation mel'.split(' '):
    #    compare.compare(args.project_path, args.project, what_to_compare)
    print(time.asctime())
else:
    print(f'unknown command {command_args.command}')
