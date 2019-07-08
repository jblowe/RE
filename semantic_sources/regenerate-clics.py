import subprocess
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from projects import projects

for project_name, path in projects.items():
    mel_path = os.path.join('../', path, f'{project_name}.clics.mel.xml')
    subprocess.check_output(f'python3 ../all_glosses.py {project_name} | python3 clics.py {sys.argv[1]} > {mel_path}', shell=True)
