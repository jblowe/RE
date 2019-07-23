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
            cli = [os.path.join(project, experiment)]
            if 'name' in parameters: cli.append(f"-r{parameters['name']}")
            if 'mel' in parameters: cli.append(f"-m{parameters['mel']}" )
            if parameters['strict'] == 'yes': cli.append('-w')
            os.chdir(os.path.join('..', 'src'))
            # p_object = subprocess.call(['git', 'pull', '-v'])
            print(['python3', 'REcli.py'] + cli)
            p_object = subprocess.call(['python3', 'REcli.py'] + cli)
            # (re)run compare
            p_object = subprocess.call(['python3', 'REcli.py', cli[0], '-x'])
            os.chdir(os.path.join('..', 'REwww'))
        elapsed_time = time.time() - elapsed_time
        return '{:.2f}'.format(elapsed_time), '(Re)run succeeded', True
    except:
        raise
        return '{:.2f}'.format(elapsed_time), 'Upstream run failed.', False
