import utils
import read
from argparser import args, need_to_compare, project_dir

settings = read.read_settings_file(f'../{project_dir}/{args.project}.default.parameters.xml',
                                   mel=args.mel,
                                   recon=args.recon)

for gloss in utils.all_glosses(read.read_attested_lexicons(settings)):
    print(gloss)
