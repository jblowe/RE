import os


def get_dirs(root):
    directories = {}
    base_dir = os.path.join('..', root)
    # if a directory has a ".master.parameters.xml" file in it, it is a corpus
    for root, dirs, files in os.walk(base_dir):
        for d in sorted(dirs):
            if os.path.isfile(os.path.join(base_dir, d, f'{d}.master.parameters.xml')):
                directories[d] = os.path.join(base_dir, d)
        break
    return directories


def find_path(root, path):
    base_dir = os.path.join('..', root)
    if path == 'all':
        return get_dirs(root)
    elif os.path.isdir(os.path.join(base_dir, path)):
        return os.path.join(base_dir, path)
    else:
        raise Exception("Experiment not found.")

projects = get_dirs('projects')
experiments = get_dirs('experiments')
