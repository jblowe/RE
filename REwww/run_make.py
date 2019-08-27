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
                pass
            os.chdir('REwww')
        else:
            cli = [project, experiment]
            for p in 'recon fuzzy mel run'.split(' '):
                if p in parameters and parameters[p] != '':
                    cli += [f'--{p}', f'{parameters[p]}']
            if parameters['strict'] == 'yes': cli.append('-w')
            os.chdir(os.path.join('..', 'src'))
            try:
                messages.append(' '.join([PYTHON, 'REcli.py', 'upstream',] + cli))
                p_object = subprocess.call([PYTHON, 'REcli.py', 'upstream'] + cli)
            except:
                pass
            os.chdir(os.path.join('..', 'REwww'))
        elapsed_time = time.time() - elapsed_time
        if p_object == 0:
            if project == 'ALL':
                messages.append('{:.2f} seconds. "make all" succeeded.'.format(elapsed_time))
            else:
                messages.append('{:.2f} seconds. (Re)run Upstream succeeded.'.format(elapsed_time))
            return messages, True
        else:
            if project == 'ALL':
                messages.append('{:.2f} seconds. "make all" failed.'.format(elapsed_time))
            else:
                messages.append('{:.2f} seconds. Upstream run failed.'.format(elapsed_time))
            return messages, False

def compare(project, experiment1, experiment2, run1, run2):
    messages = []