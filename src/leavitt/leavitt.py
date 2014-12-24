from argparse import ArgumentError, ArgumentParser, FileType, SUPPRESS
from sys import exit, stdin, stdout, stderr
from os import path
import numpy
import pandas
from pandas import DataFrame
from pandas.io.parsers import read_table
from itertools import count
from leavitt.regression import diagonalize, svd
from leavitt.utils import convert_units, zscore

regressor_choices = {
    "svd": svd
}

sigma_choices = {
    "zscore": zscore
}

def get_args():
    parser = ArgumentParser(prog="leavitt")

    general_group    = parser.add_argument_group("General")
    output_group     = parser.add_argument_group("Optional Output")
    regression_group = parser.add_argument_group("Regression")
    outlier_group    = parser.add_argument_group("Outlier Detection")

    ## General Options ##
    general_group.add_argument("-i", "--input", type=str,
        default=stdin,
        help="Input table "
             "(default = stdin)")
    general_group.add_argument("-o", "--output", type=str,
        default=".",
        help="Output directory "
             "(default = current directory)")
    general_group.add_argument("-f", "--format", type=str,
        default="%.5f",
        help="format specifier for output "
             "(default = .5f)")
    general_group.add_argument("--sep", type=str,
        default="\s",
        help="separator in input/output tables "
             "(default = whitespace)")
    general_group.add_argument("-u", "--units", type=str,
        default="modulii", choices=["modulii", "pc", "kpc"],
        help="Distance units "
             "(default = modulii)")

    ## Output Options ##
    output_group.add_argument("--regression-input-file", type=str,
        default=None,
        help="(optionally) save regression input matrices to files with this"
             "prefix")
    output_group.add_argument("--regression-output-file", type=str,
        default=None,
        help="(optionally) save regression output matrices to files with this"
             "prefix")
    output_group.add_argument("--distance-file", type=str,
        default=None,
        help="(optionally) save fitted distances to files with this prefix")

    ## Regression Options ##
    regression_group.add_argument("-r", "--regressor", type=str,
        default="svd", choices=["svd"],
        help="Method used for solving least-squares matrix "
             "(default = svd)")

    ## Outlier Options ##
    outlier_group.add_argument("--sigma", type=float,
        default=numpy.PINF,
        help="rejection criterion for outliers "
             "(default = infinity)")
    outlier_group.add_argument("--sigma-method", metavar="M", type=str,
        default="zscore", choices=["zscore"],
        help="sigma clipping method to use "
             "(default = standard)")

    args = parser.parse_args()

    args.regressor = regressor_choices[args.regressor]
    args.sigma_method = sigma_choices[args.sigma_method]

    return args

def main(args=None):
    if args is None:
        args = get_args()

    data = read_table(args.input, index_col=0, sep=args.sep,
                      engine="python")


    data["dist_0"] = convert_units(args.regressor(diagonalize(data)),
                                   args.units)
    for iteration in count(start=1):
        prev_label = "dist_{}".format(iteration-1)
        prev_selected = data.loc[~numpy.isnan(data[prev_label])]
        arg_selected = (prev_selected[[prev_label]].values
                        < args.sigma).flatten()
        next_selected = prev_selected.loc[arg_selected]

        # finished sigma clipping
        if prev_selected.shape == next_selected.shape:
            break

        next_label = "dist_{}".format(iteration)
        data[next_label] = convert_units(
            args.regressor(diagonalize(next_selected)),
            args.units)

    data.to_csv(stdout, sep="\t")

    return 0

if __name__ == "__main__":
    exit(main())
