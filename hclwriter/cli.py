#!/usr/bin/env python

# TODO: something like this?

from argparse import ArgumentParser


parser = ArgumentParser(description='cli interface for hclwriter')
parser.add_argument(
    'file',
    help='file to execute to generate .tf'
)
parser.add_argument(
    '-c', '--commands',
    # TODO: tf -h lotsa commands...
    nargs='+', choices=['init', 'fmt', 'validate', 'plan', 'apply', 'destroy'],
    help='tf commands to run after file generation',
)
args = parser.parse_args()

print(args)
