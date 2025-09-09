import subprocess
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from projects import projects

# run this from the parent directory

for project_name, path in projects.items():
    print(f'regenerating clics for {project_name}')
    mel_path = os.path.join(path, f'{project_name}.clics.mel.xml')
    not_found_path = os.path.join(path, f'{project_name}.clics.notfound.mel.xml')
    subprocess.check_output(f'python REcli.py list-all-glosses {project_name} | sort | python semantic_sources/clics.py {sys.argv[1]} > {mel_path}', shell=True)
