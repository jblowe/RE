import subprocess
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from projects import projects

# run this from the parent directory

for project_name, path in projects.items():
    print(f'regenerating wordnet mels for {project_name}')
    mel_path = os.path.join(path, f'{project_name}.wordnet.mel.xml')
    subprocess.check_output(f'python REcli.py list-all-glosses {project_name} | sort | python semantic_sources/wnlookup.py > {mel_path}', shell=True)
