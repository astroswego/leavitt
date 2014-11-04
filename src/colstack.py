import numpy
from argparse import ArgumentParser
from sys import stdin, stdout

def get_args():
    parser = ArgumentParser()

    parser.add_argument("-i", "--input", type=str,
        default=None,
        help="input file, or left blank to read from stdin")
    parser.add_argument("-c", "--columns", type=int, metavar="C",
        nargs="+",
        help="indices of columns to stack")
    parser.add_argument("--header",
        action="store_true", default=False,
        help="input contains header")
    parser.add_argument("--header-replacement", type=str,
        default=None,
        help="use when input contains header. "
             "replaces output column header with given string. "
             "if none given, uses the first column's header")
    parser.add_argument('--encoding', type=str,
        default='utf-8',
        help='file encoding (default is utf-8)')
    parser.add_argument("--sep", type=str,
        default=None,
        help="separator character in input file (default is all whitespace)")

    args = parser.parse_args()

    if args.input is None:
        args.input = stdin

    args.header_replacement = (args.header_replacement and
                               args.header_replacement.encode())

    return args

def main():
    args = get_args()

    in_table = numpy.loadtxt(args.input, dtype=bytes, delimiter=args.sep,
                             usecols=args.columns)

    if args.header:
        header   = args.header_replacement or in_table[0,0]
        in_table = in_table[1:]

    columns = in_table.T

    if args.header:
        print(header.decode(args.encoding))

    for column in columns:
        for entry in column:
            print(entry.decode(args.encoding))

    return 0

if __name__ == '__main__':
    exit(main())
