import read
import RE
import sys
import time
import coverage
import load_hooks
from argparser import args, need_to_compare, project_dir

print(time.asctime())

load_hooks.load_hook(args.project)
settings = read.read_settings_file(f'{project_dir}/{args.project}.{args.run}.parameters.xml',
                                   mel=args.mel,
                                   recon=args.recon)

print(f'{project_dir}/{args.project}.{args.run}.parameters.xml')

attested_lexicons = read.read_attested_lexicons(settings)

if args.coverage:
    if args.mel == 'none':
        print('no mel provided')
        sys.exit(1)
    print(f'checking {args.project} glosses in {args.mel} mel:')
    coverage.check_mel_coverage(settings)
else:
    B = RE.batch_all_upstream(settings, attested_lexicons=attested_lexicons)

    if need_to_compare:
        settings2 = read.read_settings_file(f'{project_dir}/{args.project}.{args.run}.parameters.xml',
                                        mel=(args.mel2 or args.mel),
                                        recon=(args.recon2 or args.recon))
        B2 = RE.batch_all_upstream(settings2, attested_lexicons=attested_lexicons)
        analysis_file = f'{project_dir}/{args.project}.{args.run}.analysis.txt'
        RE.analyze_sets(B, B2, analysis_file)
        print(f'wrote analysis to {analysis_file}')
    else:
        #print_sets(B)
        keys_file = f'{project_dir}/{args.project}.{args.run}.keys.txt'
        RE.dump_keys(B, keys_file)
        print(f'wrote keys to {keys_file}')
        sets_file = f'{project_dir}/{args.project}.{args.run}.sets.txt'
        RE.dump_sets(B, sets_file)
        print(f'wrote text sets to {sets_file}')
        sets_xml_file = f'{project_dir}/{args.project}.{args.run}.sets.xml'
        RE.dump_xml_sets(B, sets_xml_file)
        print(f'wrote {len(B.forms)} xml sets to {sets_xml_file}')
        failures_xml_file = f'{project_dir}/{args.project}.{args.run}.failures.sets.xml'
        C = RE.extract_failures(B)
        RE.dump_xml_sets(C, failures_xml_file)
        print(f'wrote {len(C.statistics.failed_parses)} failures to {failures_xml_file}')
        isolates_xml_file = f'{project_dir}/{args.project}.{args.run}.isolates.sets.xml'
        C, forms_used = RE.extract_isolates(B)
        RE.dump_xml_sets(C, isolates_xml_file)
        print(f'{len(forms_used)} different reflexes in cognate sets')
        print(f'wrote {len(C.forms)} isolates to {isolates_xml_file}')

print(time.asctime())
