from argparse import ArgumentError, ArgumentParser, FileType, SUPPRESS
from sys import exit, stdin, stdout, stderr
from os import path
import numpy
import pandas
from pandas import DataFrame
from pandas.io.parsers import read_table
from itertools import chain, count, product
from leavitt.regression import distance_formula, svd
from leavitt.utils import convert_units, zscore

sigma_choices = {
    "zscore": zscore
}

def add_coeff_rows(frame, independent_vars, dependent_vars, add_const,
                   **kwargs):
    if add_const:
        independent_vars = chain(independent_vars, ["const"])
    for (dep, ind) in product(dependent_vars, independent_vars):
        coeff_name = "{}_{}".format(ind, dep)
        frame.loc[coeff_name] = numpy.nan
    

def get_args():
    parser = ArgumentParser(prog="leavitt")

    general_group    = parser.add_argument_group("General")
    regression_group = parser.add_argument_group("Regression")
    outlier_group    = parser.add_argument_group("Outlier Detection")

    ## General Options ##
    general_group.add_argument("-i", "--input", type=str,
        default=stdin,
        help="Input table "
             "(default = stdin)")
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
    general_group.add_argument("-m", "--mean-modulus", type=float,
        default=0.0,
        help="Mean distance modulus of target, to be added to the obtained "
             "modulii "
             "(default = 0.0)")

    ## Regression Options ##
    regression_group.add_argument("--dependent-vars", type=str, nargs="+",
        metavar="VAR",
        help="List of dependent variables to regress on")
    regression_group.add_argument("--independent-vars", type=str, nargs="+",
        metavar="VAR",
        help="List of independent variables to regress on")
    regression_group.add_argument("--add-const", action="store_true",
        default=False,
        help="Add a constant term to each equation")

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

    args.sigma_method = sigma_choices[args.sigma_method]

    return args

def main(args=None):
    if args is None:
        args = get_args()

    data = read_table(args.input, index_col=0, sep=args.sep,
                      engine="python")
    add_coeff_rows(data, **vars(args))
    n_coeff = len(args.dependent_vars) * (len(args.independent_vars)
                                        + args.add_const)

    y, A = distance_formula(data.dropna(),
                            args.dependent_vars, args.independent_vars,
                            args.add_const)

#    x = numpy.linalg.lstsq(A, y, rcond=1)[0]
    x = svd(A, y)
    x[:-n_coeff] = convert_units(x[:-n_coeff]+args.mean_modulus, args.units)
    data["dist_0"] = x

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
        y, A = distance_formula(next_selected,
                                args.dependent_vars, args.independent_vars,
                                args.add_const)
#        x = numpy.linalg.lstsq(A, y, rcond=1)[0]
        x = svd(A, y)
        x[:-n_coeff] = convert_units(x[:-n_coeff]+args.mean_modulus, args.units)

        data[next_label] = x

    data.to_csv(stdout, sep="\t", na_rep="NaN")

    return 0

if __name__ == "__main__":
    exit(main())
