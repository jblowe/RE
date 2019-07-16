import os

projects = {'TGTM': '../projects/TGTM',
            'ROMANCE': '../projects/ROMANCE',
            'DEMO93': '../projects/DEMO93',
            'DIS': '../projects/DIS',
            'POLYNESIAN': '../projects/POLYNESIAN',
            'LOLOISH': '../projects/LOLOISH',
            'NYI': '../projects/LOLOISH',
            'SYI': '../projects/LOLOISH',
            'GERMANIC': '../projects/GERMANIC',
            'VANUATU': '../projects/VANUATU',
            'RE_DATA_1994': '../projects/RE_DATA_1994'
            }

def find_project_path(project):
    if project == 'all':
        return projects
    else:
        path = os.path.join('..', 'projects', project)
        return path