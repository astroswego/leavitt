import math
import numpy
from itertools import cycle, repeat
from argparse import ArgumentError, ArgumentParser, SUPPRESS
from sys import stdin, stdout, stderr
import csv

def get_args():
    parser = ArgumentParser()
    # create groups?

    parser.add_argument('-i', '--input', type=str,
        default=None,
        help='input file, or left blank to read from stdin')
    parser.add_argument('-f', '--format', type=str,
        default='%.5f',
        help='format specifier for output table')
    parser.add_argument('-n', '--number-of-groups', dest='n_groups', type=int,
        default=1,
        help='number of groups of variables to separate')
    parser.add_argument('--header',
        action='store_true', default=False,
        help='input contains header, which should be preserved')
    parser.add_argument('--row-names',
        action='store_true', default=False,
        help='input contains row names, which should be preserved')
    parser.add_argument('--encoding', type=str,
        default='utf-8',
        help='file encoding (default is utf-8)')
    parser.add_argument('--fill', type=str,
        default='0',
        help='character to fill empty spaces')
    parser.add_argument('--sep', type=str,
        default=None,
        help='separator character in input file (default is all whitespace)')
    parser.add_argument('--output-sep', type=str,
        default='\t',
        help='separator character in output file (default is tab)')

    args = parser.parse_args()

    if args.input is None:
        args.input = stdin

    return args

def main():
    args = get_args()

    in_table = numpy.loadtxt(args.input, dtype=bytes)

    if args.header:
        header   = in_table[0]
        in_table = in_table[1:]
    if args.row_names:
        row_names = in_table[:,0]
        in_table  = in_table[:,1:]
    else:
        row_names = repeat(None)

    
    diagonalized_table = diagonalize(in_table, args.n_groups)

    formatter = lambda x: format_bytes(x, fill=args.fill,
                                       encoding=args.encoding)
    if args.header:
        print(*map(formatter, header), sep=args.output_sep)
    for name, row in zip(cycle(row_names), diagonalized_table):
        if name is not None:
            print(formatter(name), end=args.output_sep)
        print(*map(formatter, row), sep=args.output_sep)

    return 0

def diagonalize(table, n_groups):
    rows, cols = table.shape
    assert cols % n_groups == 0, \
      "Number of columns is not divisible by number of groups"
    group_size = cols // n_groups

    groups = (table[:, i*group_size : (i+1)*group_size]
              for i in range(n_groups))
    diagonalized_table = numpy.empty((rows*n_groups, cols),
                                     dtype=object)

    for i, group in enumerate(groups):
        row_begin = i*rows
        col_begin = i*group_size
        row_slice = slice(row_begin, row_begin+rows)
        col_slice = slice(col_begin, col_begin+group_size)

        diagonalized_table[row_slice, col_slice] = group

    return diagonalized_table

def format_bytes(item, *, fill, encoding):
    if item is None:
        return fill
    else:
        return item.decode(encoding)

if __name__ == '__main__':
    exit(main())
