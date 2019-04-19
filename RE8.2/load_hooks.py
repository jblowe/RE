import projects
import os
import sys

def load_hook(project):
    base_dir = projects.projects[project]
    sys.path.append('toolbox/')
    sys.path.append(base_dir)
    import hook
