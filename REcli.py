import read
import RE
import sys
import time
import coverage
import compare
import load_hooks
from argparser import args, need_to_compare, project_dir

print(time.asctime())
print('Command line options used: ' + ' '.join(sys.argv[1:]))

settings = read.read_settings_file(f'{project_dir}/{args.project}.default.parameters.xml',
                                   mel=args.mel,
                                   recon=args.recon)

print(f'{project_dir}/{args.project}.default.parameters.xml')

load_hooks.load_hook(args.project, settings)
attested_lexicons = read.read_attested_lexicons(settings)

if args.coverage:
    if args.mel == 'none':
        print('no mel provided')
        sys.exit(1)
    print(f'checking {args.project} glosses in {args.mel} mel:')
    coverage_statistics = coverage.check_mel_coverage(settings)
    coverage_xml_file = f'{project_dir}/{args.project}.{args.mel}.mel.statistics.xml'
    RE.write_xml_stats(coverage_statistics, coverage_xml_file)
elif args.compare:
    comparison = compare.compare(project_dir, args.project)
    pass
else:
    B = RE.batch_all_upstream(settings, attested_lexicons=attested_lexicons)

    if need_to_compare:
        settings2 = read.read_settings_file(f'{project_dir}/{args.project}.default.parameters.xml',
                                        mel=(args.mel2 or args.mel),
                                        recon=(args.recon2 or args.recon))
        B2 = RE.batch_all_upstream(settings2, attested_lexicons=attested_lexicons)
        analysis_file = f'{project_dir}/{args.project}.{args.run}.analysis.txt'
        evaluation_stats = RE.analyze_sets(B, B2, analysis_file)
        evaluation_stats['lexicon_1'] = str(settings.mel_filename).replace(f'{project_dir}/{args.project}.','')
        evaluation_stats['lexicon_2'] = str(settings2.mel_filename).replace(f'{project_dir}/{args.project}.','')
        print(f'wrote analysis to {analysis_file}')
        evaluation_xml_file = f'{project_dir}/{args.project}.{args.run}.evaluation.xml'
        RE.write_evaluation_stats(evaluation_stats, evaluation_xml_file)
    else:
        keys_file = f'{project_dir}/{args.project}.{args.run}.keys.csv'
        RE.dump_keys(B, keys_file)
        print(f'wrote {len(B.statistics.keys)} keys and {len(B.statistics.failed_parses)} failures to {keys_file}')
        sets_file = f'{project_dir}/{args.project}.{args.run}.sets.txt'
        RE.dump_sets(B, sets_file)
        print(f'wrote {len(B.forms)} text sets to {sets_file}')
        sets_xml_file = f'{project_dir}/{args.project}.{args.run}.sets.xml'
        RE.dump_xml_sets(B, sets_xml_file)
        print(f'wrote {len(B.forms)} xml sets to {sets_xml_file}')
        # failures (no parses)
        failures_xml_file = f'{project_dir}/{args.project}.{args.run}.failures.sets.xml'
        RE.dump_xml_sets(RE.Lexicon(B.language, [
            RE.ProtoForm('failed', (), sorted(B.statistics.failed_parses, key=lambda x: x.language)[:2000],
                         (), [])],
                         B.statistics), failures_xml_file)
        print(f'wrote {len(B.statistics.failed_parses)} failures to {failures_xml_file}')
        # isolates
        isolates_xml_file = f'{project_dir}/{args.project}.{args.run}.isolates.sets.xml'
        C, forms_used = RE.extract_isolates(B)
        C.statistics.sets = B.forms
        RE.dump_xml_sets(C, isolates_xml_file)
        C.statistics.add_stat('isolates', len(C.forms))
        C.statistics.add_stat('sets', len(B.forms))
        C.statistics.add_stat('reflexes_in_sets', len(forms_used))
        print(f'{len(forms_used)} different reflexes in cognate sets')
        print(f'wrote {len(C.forms)} isolates to {isolates_xml_file}')
        stats_xml_file = f'{project_dir}/{args.project}.{args.run}.statistics.xml'
        RE.write_xml_stats(C.statistics, stats_xml_file)

print(time.asctime())
