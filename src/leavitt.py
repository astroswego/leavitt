from sys import stdin, stdout, stderr
import numpy as np
from argparse import ArgumentError, ArgumentParser, FileType, SUPPRESS
from statsmodels.api import add_constant, OLS

def get_args():
    parser = ArgumentParser()

    parser.add_argument('-i', '--input', type=FileType('r'),
        default=stdin,
        help='input table')
    parser.add_argument('--header',
        default=False, action='store_true',
        help='input contains header')
    parser.add_argument('--use-cols', type=int, nargs='+',
        default=None,
        help='columns to use')

    args = parser.parse_args()

    return args

def main():
    args = get_args()

    data = np.loadtxt(args.input,
                      usecols=args.use_cols,
                      skiprows=(1 if args.header else 0))
    y, X = data[:,0], add_constant(data[:,1:])

    model = OLS(y, X).fit()

    print(model.summary())

    return 0

if __name__ == '__main__':
    exit(main())
