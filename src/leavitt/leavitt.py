from argparse import ArgumentError, ArgumentParser, SUPPRESS
from sys import exit, stdin, stderr
from os import path
import numpy

def get_args():
    parser = ArgumentParser(prog="leavitt")

    args = parser.parse_args()

    return args

def main():
    args = get_args()

    return 0

if __name__ == "__main__":
    exit(main())
