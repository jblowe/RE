## A place to define per-project settings dependent pre-processing steps.

import importlib.util
import os
import sys

def load_hook(project_path):
    hook_file = os.path.join(project_path, 'hook.py')
    if not os.path.isfile(hook_file):
        print('No preprocessing needed.')
        return

    # Add support paths once (idempotent)
    for p in ('toolbox/', project_path):
        if p not in sys.path:
            sys.path.insert(0, p)

    try:
        print('trying for hooks')
        # Load from the explicit file path so each project gets its own
        # module, bypassing Python's sys.modules cache entirely.
        spec = importlib.util.spec_from_file_location('_hook', hook_file)
        hook = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook)
        hook.run_load_hooks()
    except AttributeError:
        print('No preprocessing needed.')
        return
    except Exception:
        raise
