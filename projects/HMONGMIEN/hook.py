import read
import serialize
import os
import sys
from utils import cd

base_dir = os.path.dirname(__file__)

print(f'base_dir {base_dir}')

def generate_xml_data():
    print('running pipeline to generate data files')
    code_dir = os.path.join('..', '..', '..', 'src')
    with cd(os.path.join(base_dir)):
        with open('pipeline.sh', 'r', encoding='utf-8') as commands:
            for command in commands:
                if command[0] == '#': continue
                if 'perl' in command or 'python' in command:
                    command = command.replace('$1', code_dir)
                    print(command.strip())
                    exit_code = os.system(command.strip())
                    if exit_code != 0:
                        sys.exit(exit_code)

def run_load_hooks(arg, settings):
    generate_xml_data()
