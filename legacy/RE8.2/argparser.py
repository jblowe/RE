import argparse
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
parser.add_argument('--mel2',
                    metavar='mel2',
                    help='name of MEL to compare against')
parser.add_argument('--recon2',
                    metavar='recon2',
                    help='model of reconstruction to compare against')

args = parser.parse_args()
project_dir = projects.projects[args.project]
need_to_compare = (args.mel2 or args.recon2)
