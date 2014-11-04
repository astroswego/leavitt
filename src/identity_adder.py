import numpy
from argparse import ArgumentParser, SUPPRESS
from sys import stdin, stdout, stderr

def get_args():
    parser = ArgumentParser()

    parser.add_argument('-i', '--input', type=str,
        default=None,
        help='input file, or left blank to read from stdin')
    parser.add_argument('--header',
        action='store_true', default=False,
        help='input contains header, which should be preserved')
    
