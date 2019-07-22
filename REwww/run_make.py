import subprocess
import os
import time


def make(project, experiment, parameters):
    try:
        elapsed_time = time.time()
        if project == 'ALL':
            return f'make ALL is disabled for now.'
            os.chdir('..')
            p_object = subprocess.call(['git', 'pull', '-v'])
            p_object = subprocess.call(['make', '-w'])
            os.chdir('REwww')
        else:
            run = f"-r {parameters['name']}" if 'name' in parameters else ''
            mel = f"--mel {parameters['mel']}" if 'mel' in parameters else ''
            strict = '-w' if parameters['strict'] == 'yes' else ''
            os.chdir(os.path.join('..', 'src'))
            # p_object = subprocess.call(['git', 'pull', '-v'])
            print(['python3', 'REcli.py', run, strict, mel, os.path.join(project, experiment)])
            p_object = subprocess.call(['python3', 'REcli.py', run, strict, mel, os.path.join(project, experiment)])
            os.chdir(os.path.join('..', 'REwww'))
        elapsed_time = time.time() - elapsed_time
        return f'(Re)run of project {project}, experiment {experiment} completed. {elapsed_time} s.', ''
    except:
        return f'refresh from GitHub failed.', ''
