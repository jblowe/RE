import os


def _config_path() -> str:
    """Return the default projects.yaml path.

    We keep it at repo root (sibling of src/), so users can easily edit it.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, '..', 'projects.yaml')


def _parse_simple_yaml_map(text: str) -> dict:
    """Parse a very small subset of YAML:

    KEY: value
    # comments allowed

    This intentionally avoids adding a dependency on PyYAML.
    """
    out = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        # strip trailing comment
        if '#' in line:
            line = line.split('#', 1)[0].strip()
        if ':' not in line:
            continue
        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if not key or not val:
            continue
        out[key] = val
    return out


def _normalize_path(path_value: str, base_dir: str) -> str:
    # expand ~ and env vars
    p = os.path.expandvars(os.path.expanduser(path_value))
    if not os.path.isabs(p):
        p = os.path.normpath(os.path.join(base_dir, p))
    return os.path.abspath(p)


def _default_projects_map(root: str = 'projects') -> dict:
    """Fallback: enumerate immediate subdirectories under ../projects/"""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', root))
    out = {}
    if not os.path.isdir(base_dir):
        return out
    for name in sorted(os.listdir(base_dir)):
        full = os.path.join(base_dir, name)
        if os.path.isdir(full) and not name.startswith('.'):
            out[name] = full
    return out


def get_dirs(root: str = 'projects'):
    """Return a mapping of project label -> directory path.

    Primary source is projects.yaml at repo root.
    Fallback is ../projects/<NAME>/ enumeration.
    """
    cfg = _config_path()
    if os.path.isfile(cfg):
        base_dir = os.path.abspath(os.path.dirname(cfg))
        with open(cfg, 'r', encoding='utf-8') as f:
            m = _parse_simple_yaml_map(f.read())
        return {k: _normalize_path(v, base_dir) for (k, v) in m.items()}
    return _default_projects_map(root)


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