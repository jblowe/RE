import subprocess
import os
import time


def make(project_name):
    try:
        elapsed_time = time.time()
        if project_name == 'ALL':
            os.chdir('..')
            p_object = subprocess.call(['git', 'pull', '-v'])
            p_object = subprocess.call(['make', '-w'])
            os.chdir('REwww')
        else:
            os.chdir(os.path.join('..', 'src'))
            p_object = subprocess.call(['git', 'pull', '-v'])
            p_object = subprocess.call(['bash', 'testPROJECT.sh', project_name])
            os.chdir(os.path.join('..', 'REwww'))
        elapsed_time = time.time() - elapsed_time
        return f'refresh of project {project_name} from GitHub completed. {elapsed_time} s.'
    except:
        return f'refresh from GitHub failed.'
