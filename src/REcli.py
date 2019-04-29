import read
import RE
import sys
import coverage
import load_hooks
from argparser import args, need_to_compare, project_dir

load_hooks.load_hook(args.project)
settings = read.read_settings_file(f'{project_dir}/{args.project}.{args.run}.parameters.xml',
                                   mel=args.mel,
                                   recon=args.recon)

print(f'{project_dir}/{args.project}.{args.run}.parameters.xml')

if 'csvdata' in settings.attested:
    attested_lexicons = read.read_tabular_lexicons(settings, (1, 0, 2), delimiter='\t')
else:
    attested_lexicons = read.read_attested_lexicons(settings)

if args.coverage:
    if args.mel == 'none':
        print('no mel provided')
        sys.exit(1)
    print(f'{args.project} glosses not found in {args.mel} mel:')
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
        print(f'wrote keys file to {keys_file}')
        sets_file = f'{project_dir}/{args.project}.{args.run}.sets.txt'
        RE.dump_sets(B, sets_file)
        print(f'wrote sets file to {sets_file}')
