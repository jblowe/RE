import subprocess
import os
import time


def make(project, experiment, parameters):
    PYTHON = 'python'
    messages = []
    if True:
        elapsed_time = time.time()
        if project == 'ALL':
            os.chdir('..')
            try:
                p_object = subprocess.call(['git', 'pull', '-v'])
                p_object = subprocess.call(['make', '-w'])
            except:
                messages.append('{:.2f} seconds. Upstream run failed.'.format(elapsed_time))
            os.chdir('REwww')
            return messages, False
        else:
            cli = [project, experiment]
            for p in 'recon fuzzy mel run'.split(' '):
                if p in parameters and parameters[p] != '':
                    cli += [f'--{p}', f'{parameters[p]}']
            if parameters['strict'] == 'yes': cli.append('-w')
            os.chdir(os.path.join('..', 'src'))
            try:
                # p_object = subprocess.call(['git', 'pull', '-v'])
                messages.append(' '.join([PYTHON, 'REcli.py', 'upstream',] + cli))
                p_object = subprocess.call([PYTHON, 'REcli.py', 'upstream'] + cli)
            except:
                pass
            os.chdir(os.path.join('..', 'REwww'))
        elapsed_time = time.time() - elapsed_time
        if p_object == 0:
            messages.append('{:.2f} seconds. (Re)run Upstream succeeded.'.format(elapsed_time))
            return messages, True
        else:
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
            messages.append(' '.join(['python3', 'REcli.py', 'upstream',] + cli))
            p_object = subprocess.call(['python3', 'REcli.py', 'upstream'] + cli)
            # (re)run IR compare
            messages.append(' '.join(['python3', 'REcli.py', 'upstream'] + cli))
            # p_object = subprocess.call(['python3', 'upstream', 'REcli.py', 'compare', cli[0], cli[0], '-x'])
            os.chdir(os.path.join('..', 'REwww'))
        elapsed_time = time.time() - elapsed_time
        messages.append('{:.2f}'.format(elapsed_time), '(Re)run Upstream succeeded')
        return messages, True
    except:
        messages.append('{:.2f}'.format(elapsed_time), 'Upstream run failed.')
        return messages, False
