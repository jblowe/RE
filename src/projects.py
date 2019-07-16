import os


def get_dirs(root):
    directories = {}
    base_dir = os.path.join('..', root)
    for root, dirs, files in os.walk(base_dir):
        for d in sorted(dirs):
            if os.path.isfile(os.path.join(base_dir, d, f'{d}.default.parameters.xml')):
                directories[d] = os.path.join(base_dir, d)
        break
    return directories


def find_path(root, path):
    base_dir = os.path.join('..', root)
    if path == 'all':
        return get_dirs(root)
    else:
        if os.path.isdir(os.path.join(base_dir, path)):
            return os.path.join(base_dir, path)
        elif os.path.isfile(path):
            dir = os.path.dirname(os.path.join(base_dir, path))
            return dir
        elif os.path.isfile(os.path.join(base_dir, path)):
            return os.path.dirname(os.path.join(base_dir, path))
        else:
            return os.path.join(base_dir, path)


projects = get_dirs('projects')
experiments = get_dirs('experiments')