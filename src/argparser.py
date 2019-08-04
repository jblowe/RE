import argparse
import os
import projects
import sys

def raise_unknown_command(command):
    raise Exception(f'Unknown command {command}')

def parse_run():
    parser = argparse.ArgumentParser(description='Run a project.')
    parser.add_argument('project',
                        metavar='project',
                        help='name of the project')
    parser.add_argument('experiment',
                        metavar='experiment',
                        help='experiment to run')
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
    return parser

def parse_compare():
    parser = argparse.ArgumentParser(description='Compare or Diff two runs')
    parser.add_argument('project',
                        metavar='project',
                        help='name of the project')
    parser.add_argument('experiment1')
    parser.add_argument('experiment2')
    parser.add_argument('-r1', '--run1',
                        metavar='run1',
                        default='default',
                        help='name of the run')
    parser.add_argument('-r2', '--run2',
                        metavar='run2',
                        default='default',
                        help='name of the run')
    return parser

def parse_new_experiment():
    parser = argparse.ArgumentParser(description='Make a new experiment')
    parser.add_argument('project')
    parser.add_argument('experiment_name')
    return parser

def parse_coverage():
    parser = argparse.ArgumentParser(description='Compute mel coverage')
    parser.add_argument('project')
    parser.add_argument('experiment')
    parser.add_argument('mel_name')
    return parser

command_parser = argparse.ArgumentParser(description='The Reconstruction Engine.')
command_parser.add_argument('command', help='Subcommand to run')
command_args = command_parser.parse_args(sys.argv[1:2])

parser = (parse_run() if command_args.command == 'run'
          else parse_compare() if command_args.command in 'compare diff'.split(' ')
          else parse_coverage() if command_args.command == 'coverage'
          else parse_new_experiment() if command_args.command == 'new-experiment'
          else raise_unknown_command(command_args.command))

args = parser.parse_args(sys.argv[2:])

if command_args.command == 'run' or command_args.command == 'coverage':
    args.experiment_path = projects.find_path(
        'experiments',
        os.path.join(args.project, args.experiment))

if command_args.command == 'run':
    args.need_to_compare = (args.mel2 or args.recon2)

if command_args.command == 'compare' or command_args.command == 'diff':
    args.experiment_path1 = projects.find_path(
        'experiments',
        os.path.join(args.project, args.experiment1))
    args.experiment_path2 = projects.find_path(
        'experiments',
        os.path.join(args.project, args.experiment2))
