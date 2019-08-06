import os
import utils
import read
from argparser import args

# invoke as: python3 all_glosses.py upstream DIS semantics

settings = read.read_settings_file(os.path.join(args.experiment_path,f'{args.project}.master.parameters.xml'))

for gloss in utils.all_glosses(read.read_attested_lexicons(settings)):
    print(gloss)
