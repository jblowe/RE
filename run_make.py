import subprocess
import os
import time


def make(project, experiment, parameters):
    messages = []
    try:
        elapsed_time = time.time()
        if project == 'ALL':
            messages.append(f'make ALL is disabled for now.')
            return messages
            os.chdir('..')
            p_object = subprocess.call(['git', 'pull', '-v'])
            p_object = subprocess.call(['make', '-w'])
            os.chdir('REwww')
        else:
            cli = [project, experiment]
            if 'name' in parameters: cli.append(f"-r{parameters['name']}")
            if 'mel' in parameters: cli.append(f"-m{parameters['mel']}" )
            if parameters['strict'] == 'yes': cli.append('-w')
            # REcli.py compare TGTM experiment1 experiment1 --run1 with-hand --run2 with-clics
            os.chdir(os.path.join('..', 'src'))
            # p_object = subprocess.call(['git', 'pull', '-v'])
            messages.append(' '.join(['python3', 'REcli.py', 'run',] + cli))
            p_object = subprocess.call(['python3', 'REcli.py', 'run'] + cli)
            os.chdir(os.path.join('..', 'REwww'))
        elapsed_time = time.time() - elapsed_time
        messages.append('{:.2f} seconds. (Re)run Upstream succeeded.'.format(elapsed_time))
        return messages, True
    except:
        messages.append('{:.2f} seconds. Upstream run failed.'.format(elapsed_time))
        return messages, False

def compare(project, experiment1, experiment2, run1, run2):
    messages = []
    try:
        elapsed_time = time.time()
        if project == 'ALL':
            messages.append(f'make ALL is disabled for now.')
            return messages
            os.chdir('..')
            p_object = subprocess.call(['git', 'pull', '-v'])
            p_object = subprocess.call(['make', '-w'])
            os.chdir('REwww')
        else:
            cli = []
            if 'name' in parameters: cli.append(f"-r{parameters['name']}")
            if 'mel' in parameters: cli.append(f"-m{parameters['mel']}" )
            if parameters['strict'] == 'yes': cli.append('-w')
            # REcli.py compare TGTM experiment1 experiment1 --run1 with-hand --run2 with-clics
            cli = [project, experiment]
            os.chdir(os.path.join('..', 'src'))
            # p_object = subprocess.call(['git', 'pull', '-v'])
            messages.append(' '.join(['python3', 'REcli.py', 'run',] + cli))
            p_object = subprocess.call(['python3', 'REcli.py', 'run'] + cli)
            # (re)run IR compare
            messages.append(' '.join(['python3', 'REcli.py', 'run'] + cli))
            # p_object = subprocess.call(['python3', 'run', 'REcli.py', 'compare', cli[0], cli[0], '-x'])
            os.chdir(os.path.join('..', 'REwww'))
        elapsed_time = time.time() - elapsed_time
        messages.append('{:.2f}'.format(elapsed_time), '(Re)run Upstream succeeded')
        return messages, True
    except:
        messages.append('{:.2f}'.format(elapsed_time), 'Upstream run failed.')
        return messages, False
