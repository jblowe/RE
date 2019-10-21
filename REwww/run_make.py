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


def compare(project, experiment, runs):
    PYTHON = 'python'
    messages = []

    elapsed_time = time.time()
    os.chdir(os.path.join('..', 'src'))
    p_object = -1
    try:
        # time python3 REcli.py compare ${PROJECT} ${EXPERIMENT} ${EXPERIMENT} --run1 $1 --run2 $2
        cli = [project, experiment, experiment]
        cli += ['--run1', runs[0]]
        cli += ['--run2', runs[1]]
        messages.append(' '.join([PYTHON, 'REcli.py', 'compare', ] + cli))
        p_object = subprocess.call([PYTHON, 'REcli.py', 'compare'] + cli)
    except:
        pass
    os.chdir(os.path.join('..', 'REwww'))
    elapsed_time = time.time() - elapsed_time
    if p_object == 0:
        messages.append('{:.2f} seconds. "compare" succeeded.'.format(elapsed_time))
        return messages, True
    else:
        messages.append('{:.2f} seconds. "compare" failed.'.format(elapsed_time))
        return messages, False
