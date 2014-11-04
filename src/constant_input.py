import numpy
from argparse import ArgumentParser, SUPPRESS
from itertools import chain, cycle, islice, repeat, tee
from sys import stdin

def get_args():
    parser = ArgumentParser()

    parser.add_argument('-i', '--input', type=str,
        default=None,
        help='input file, or left blank to read from stdin')
    parser.add_argument('-c', '--columns', type=int, nargs='+',
        help='list of columns to insert into')
    parser.add_argument('--const', type=bytes,
        default=b'1',
        help='constant value to insert')
    parser.add_argument('--header',
        action='store_true', default=False,
        help='input contains header, which should be preserved')
    parser.add_argument('--header-prefix', type=str,
        default='X',
        help='prefix for column headings for new columns (default is "X")')
    parser.add_argument('--encoding', type=str,
        default='utf-8',
        help='file encoding (default is utf-8)')
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

    n_new_cols = len(args.columns)

    in_table = numpy.loadtxt(args.input, dtype=bytes, delimiter=args.sep)

    if args.header:
        header   = in_table[0]
        in_table = in_table[1:]

    rows, cols = in_table.shape
    const_column = numpy.empty((rows, 1), dtype=object)
    const_column.fill(args.const)

    column_separators = chain([0], args.columns, [None])
    column_pairs = list(pairwise(column_separators))
    column_groups = map(lambda indices:
                        slice_array_columnwise(in_table, *indices),
                        column_pairs)
    out_body = numpy.hstack(roundrobin(column_groups,
                                       repeat(const_column, n_new_cols)))

    formatter = lambda x: x.decode(args.encoding)

    if args.header:
        header_groups = (header[start:stop] for start, stop in column_pairs)
        out_header = chain(*roundrobin(decode_arrays(header_groups,
                                                     encoding=args.encoding),
                                       map(lambda i:
                                           ['{}{}'.format(args.header_prefix,
                                                          i)],
                                           range(n_new_cols))))
        print(*out_header, sep=args.output_sep)

    for row in out_body:
        print(*map(formatter, row), sep=args.output_sep)

    return 0

def slice_array_columnwise(array, start, stop):
    return array[:, start:stop] if stop is not None else array[:, start:]

def pairwise(iterable):
    '''s -> (s0,s1), (s1,s2), (s2, s3), ...
    (taken from itertools documentation)
    '''
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def roundrobin(*iterables):
    '''roundrobin('ABC', 'D', 'EF') --> A D E B F C
    (taken from itertools documentation)
    '''
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

def interleave(iterable, separator):
    return roundrobin(iterable, repeat(separator, len(iterable)-1))

def decode_arrays(arrays, *, encoding):
    return [[s.decode(encoding) for s in a]
            for a in arrays]

if __name__ == '__main__':
    exit(main())
