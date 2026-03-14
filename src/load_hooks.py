## A place to define per-project settings dependent pre-processing steps.

import projects
import os
import sys

def load_hook(project_path):
    sys.path.append('toolbox/')
    sys.path.append(project_path)
    try:
        print('trying for hooks')
        from hook import run_load_hooks
        run_load_hooks()

    except ModuleNotFoundError:
        print('No preprocessing needed.')
