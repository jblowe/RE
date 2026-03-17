import os

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def _config_path() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, '..', 'projects.toml')


def _normalize_path(path_value: str, base_dir: str) -> str:
    p = os.path.expandvars(os.path.expanduser(path_value))
    if not os.path.isabs(p):
        p = os.path.normpath(os.path.join(base_dir, p))
    return os.path.abspath(p)


def get_dirs(root: str = 'projects'):
    """Return a mapping of project label -> directory path.

    Primary source is projects.toml at repo root.
    """
    cfg = _config_path()
    try:
        if os.path.isfile(cfg):
            base_dir = os.path.abspath(os.path.dirname(cfg))
            with open(cfg, 'rb') as f:
                m = tomllib.load(f)
            return {k: _normalize_path(v, base_dir) for k, v in m.items()}
    except Exception:
        raise Exception(f'Could not find or perhaps parse {cfg}')


def find_path(root: str, path: str):
    """Resolve a project label to a directory.

    root is kept for backward compatibility with older callers.
    """
    projects_map = get_dirs(root)
    if path == 'all':
        return projects_map
    if path in projects_map:
        resolved = projects_map[path]
        if not os.path.isdir(resolved):
            raise Exception(f"Project '{path}' path does not exist: {resolved}")
        return resolved
    # Backward-compatible fallback: treat `path` as a literal directory under ../<root>/
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', root))
    candidate = os.path.join(base_dir, path)
    if os.path.isdir(candidate):
        return os.path.abspath(candidate)
    raise Exception("project not found.")


# keep legacy module-level vars
projects = get_dirs('projects')
