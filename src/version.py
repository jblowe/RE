"""Single source of truth for the RE version string shown in REwww and REgtk.

Resolution order:

1. Running from a git checkout  -> derived from ``git describe``:
     on a release tag            2.0.1-rc1
     N commits after a tag       2.0.1-rc1+73.g7f49fd6   (SemVer build metadata)
     uncommitted changes         ...  with a trailing ``.dirty``
     no tag reachable            7f49fd6 (bare commit hash)
2. Not a git checkout (installed copy, tarball) -> contents of the VERSION file
   at the repo root, which ``cz bump`` keeps in sync with the tag.
3. Neither available             -> "unknown"

Only numeric tags (2.0.0, 2.0.1-rc1, ...) are considered, so the rolling
"latest" pre-release tag that the installer workflow moves is ignored.
"""
import os
import re
import subprocess
from functools import lru_cache

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# git describe --long output: <tag>-<n>-g<hash>[-dirty]
_DESCRIBE_RE = re.compile(r'^(?P<tag>.+)-(?P<n>\d+)-g(?P<hash>[0-9a-f]+)(?P<dirty>-dirty)?$')


def _from_git():
    if not os.path.exists(os.path.join(REPO_ROOT, '.git')):
        return None
    try:
        out = subprocess.run(
            ['git', 'describe', '--tags', '--match', '[0-9]*', '--long', '--always', '--dirty'],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=5, check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    if not out:
        return None
    m = _DESCRIBE_RE.match(out)
    if not m:
        # --always fallback: bare hash, optionally with -dirty
        return out.replace('-dirty', '.dirty')
    dirty = '.dirty' if m.group('dirty') else ''
    if m.group('n') == '0' and not dirty:
        return m.group('tag')                      # exactly on a tag
    if m.group('n') == '0':
        return f"{m.group('tag')}+dirty"
    return f"{m.group('tag')}+{m.group('n')}.g{m.group('hash')}{dirty}"


def _from_file():
    try:
        with open(os.path.join(REPO_ROOT, 'VERSION'), encoding='utf-8') as f:
            return f.read().strip() or None
    except OSError:
        return None


@lru_cache(maxsize=1)
def get_version():
    return _from_git() or _from_file() or 'unknown'


if __name__ == '__main__':
    print(get_version())
