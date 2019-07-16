## A place to define per-project settings dependent pre-processing steps.

import projects
import os
import sys

def load_hook(experiment_path, settings):
    sys.path.append('toolbox/')
    sys.path.append(experiment_path)
    try:
        print('trying for hooks')
        from hook import run_load_hooks
        run_load_hooks(settings)

    except ModuleNotFoundError:
        print('No preprocessing needed.')
