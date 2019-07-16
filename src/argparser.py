import argparse
import os
import projects

parser = argparse.ArgumentParser(description='The Reconstruction Engine.')
parser.add_argument('project',
                    metavar='project',
                    help='name of the project')
parser.add_argument('-t', '--recon',
                    metavar='recon',
                    default='default',
                    help='the model of reconstruction')
parser.add_argument('-m', '--mel',
                    metavar='mel',
                    default='none',
                    help='name of the MEL desired')
parser.add_argument('-r', '--run',
                    metavar='run',
                    default='default',
                    help='name of the run')
parser.add_argument('-c',
                    dest='coverage',
                    nargs='?',
                    const=True,
                    metavar='coverage',
                    help='specify for a coverage report for the specified MEL')
parser.add_argument('-x',
                    dest='compare',
                    nargs='?',
                    default=False,
                    const=True,
                    metavar='compare',
                    help='specify to compare statistics files')
parser.add_argument('-w', '--only-with-mel',
                    dest='only_with_mel',
                    nargs='?',
                    default=False,
                    const=True,
                    metavar='only_with_mel',
                    help='only keep sets which match a MEL')
parser.add_argument('--mel2',
                    metavar='mel2',
                    help='name of MEL to compare against')
parser.add_argument('--recon2',
                    metavar='recon2',
                    help='model of reconstruction to compare against')

args = parser.parse_args()
args.project_dir = projects.find_project_path(args.project)
args.project_path = args.project
args.project = args.project.split(os.sep)[0]
need_to_compare = (args.mel2 or args.recon2)
compare_results = args.compare
only_with_mel = args.only_with_mel