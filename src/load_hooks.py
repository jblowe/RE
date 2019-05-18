## A place to define per-project settings dependent pre-processing steps.

import projects
import os
import sys

def load_hook(project, settings, attested_lexicons):
    base_dir = projects.projects[project]
    sys.path.append('toolbox/')
    sys.path.append(base_dir)
    try:
        from hook import run_load_hooks
        run_load_hooks(settings, attested_lexicons)

    except ModuleNotFoundError:
        print('No preprocessing needed.')
