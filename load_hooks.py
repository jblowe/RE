## A place to define per-project settings dependent pre-processing steps.

import projects
import os
import sys

def load_hook(project, settings):
    base_dir = projects.find_project_path(project)
    sys.path.append('toolbox/')
    sys.path.append(base_dir)
    try:
        print('trying for hooks')
        from hook import run_load_hooks
        run_load_hooks(settings)

    except ModuleNotFoundError:
        print('No preprocessing needed.')
