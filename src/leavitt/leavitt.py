from argparse import ArgumentError, ArgumentParser, FileType, SUPPRESS
from sys import argv, exit, stdin, stdout, stderr
from os import path
import numpy
import pandas
from pandas import DataFrame
from pandas.io.parsers import read_table
from itertools import chain, product
from leavitt.regression import leavitt_law
from leavitt.error import monte_carlo
from leavitt.utils import (any_nan, char, identity, modulii2pc, modulii2kpc,
                           zscore)

unit_conversion_choices = {
    "modulii" : identity,
    "pc"      : modulii2pc,
    "kpc"     : modulii2kpc
}
error_choices = {
    "None" : None,
    "Monte_Carlo" : monte_carlo
}

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

def get_args(argv=argv[1:]):
    parser = ArgumentParser(prog="leavitt")

    general_group    = parser.add_argument_group("General")
    parallel_group   = parser.add_argument_group("Parallel")
    format_group     = parser.add_argument_group("Formatting")
    regression_group = parser.add_argument_group("Regression")
    outlier_group    = parser.add_argument_group("Outlier Detection")
    error_group      = parser.add_argument_group("Error Analysis")

    ## General Options ##
    general_group.add_argument("-i", "--input", type=str,
        default=stdin,
        help="Input table "
             "(default = stdin)")
    general_group.add_argument("-u", "--units", type=str,
        default="modulii", choices=["modulii", "pc", "kpc"],
        help="Distance units "
             "(default = modulii)")
    general_group.add_argument("-m", "--mean-modulus", type=float,
        default=0.0,
        help="Mean distance modulus of target, to be added to the obtained "
             "modulii "
             "(default = 0.0)")
    general_group.add_argument("--debug", action="store_true",
        help="Enable debug output")

    ## Parallel Options ##
    parallel_group.add_argument("--error-processes", type=int,
        default=1,
        help="Number of processes to use in error determination "
             "(default = 1)")

    ## Formatting Options ##
    format_group.add_argument("-f", "--format", type=str,
        default="%.5f",
        help="Format specifier for output "
             "(default = .5f)")
    format_group.add_argument("--sep", type=str,
        default="\s+",
        help="Separator in input tables (can be a regular expression) "
             "(default = whitespace)")
    format_group.add_argument("--output-sep", type=char,
        default="\t",
        help="Separator in output tables (a single character) "
             "(default = \t)")
    format_group.add_argument("--na-values", type=str, nargs="+",
        default=["NA"],
        help="String(s) used to denote N/A values in input table "
             "(default = NA)")
    format_group.add_argument("--output-na-value", type=str,
        default="NA",
        help="String used to denote N/A values in output table "
             "(default = NA)")
    format_group.add_argument("--distance-label", type=str, metavar="LABEL",
        default="dist",
        help="Label for all distance columns. "
             "Columns are titled LABEL_0 ... LABEL_N, "
             "and LABEL_N is duplicated as just LABEL "
             "(default = dist)")

    ## Regression Options ##
    regression_group.add_argument("--dependent-vars", type=str, nargs="+",
        metavar="VAR", required=True,
        help="List of dependent variables to regress on")
    regression_group.add_argument("--independent-vars", type=str, nargs="+",
        metavar="VAR", required=True,
        help="List of independent variables to regress on")
    regression_group.add_argument("--add-const", action="store_true",
        help="Add a constant term to each equation")
    regression_group.add_argument("--fit-modulus", action="store_true",
        help="Fit individual distance modulii")
    regression_group.add_argument("--rcond", type=float,
        default=1e-3,
        help="Singular values are set to zero if they are smaller than "
             "`rcond` times the largest singular value "
             "(default = 1e-3)")

    ## Outlier Options ##
    outlier_group.add_argument("--sigma", type=float,
        default=0,
        help="rejection criterion for outliers "
             "(default = infinity)")
    outlier_group.add_argument("--sigma-method", metavar="M", type=str,
        default="zscore", choices=["zscore"],
        help="sigma clipping method to use "
             "(default = standard)")
    outlier_group.add_argument("--sigma-max-iter", metavar="N", type=int,
        default=20,
        help="maximum number of iterations to use in sigma clipping "
             "(default = 20)")

    ## Error Analysis Options ##
    error_group.add_argument("--error-method", type=str, metavar="METHOD",
        default="None", choices=["Monte_Carlo", "None"],
        help="method used for computing errors on distances "
             "(default = None)")
    error_group.add_argument("--error-prefix", type=str,
        default="",
        help="columns whose names match a variable with this prefix will be "
             "used for error calculations. "
             "can be combined with --error-suffix. "
             "one of the two must be used if --error-method is not None "
             "(default = no prefix)")
    error_group.add_argument("--error-suffix", type=str,
        default="",
        help="columns whose names match a variable with this suffix will be "
             "used for error calculations. "
             "can be combined with --error-prefix. "
             "one of the two must be used if --error-method is not None "
             "(default = no suffix)")
    error_group.add_argument("--error-iterations", type=int,
        default=1000,
        help="number of iterations to use in the error determination, "
             "if applicable "
             "(default = 1000)")

    args = parser.parse_args(argv)

    args.error_method = error_choices[args.error_method]
    if args.error_method is not None \
       and args.error_prefix == args.error_suffix == "":
            raise ArgumentError("An error prefix or suffix must be provided "
                                "for error to be computed")
    args.distance_error_label = args.error_prefix   \
                              + args.distance_label \
                              + args.error_suffix

    args.sigma_method = sigma_choices[args.sigma_method]

    args.units = unit_conversion_choices[args.units]

    return args

def main(args=None):
    if args is None:
        args = get_args()

    data = read_table(args.input, index_col=0,
                      sep=args.sep, na_values=args.na_values,
                      engine="python")
    add_coeff_rows(data,
                   args.independent_vars, args.dependent_vars, args.add_const)
    n_coeff = len(args.dependent_vars) \
            * (len(args.independent_vars) + args.add_const)

    try:
        dependent_vars   = data[args.dependent_vars  ].iloc[:-n_coeff].values
        independent_vars = data[args.independent_vars].iloc[:-n_coeff].values
    except KeyError as e:
        key = e.args[0]
        print("Missing entry in input table for variable(s): {}".format(key),
              file=stderr)
        return 1

    try:
        dependent_vars_error = data[
            [args.error_prefix + var + args.error_suffix
             for var in args.dependent_vars]
        ].iloc[:-n_coeff].values

    except KeyError as e:
        key = e.args[0]
        print("Missing entry in input table for error: {}".format(key),
              file=stderr)
        return 1

    nan_rows = any_nan(dependent_vars,
                       independent_vars,
                       dependent_vars_error,
                       axis=1)
    non_nan_rows = ~nan_rows
    dependent_vars       =   dependent_vars[    non_nan_rows]
    independent_vars     = independent_vars[    non_nan_rows]
    dependent_vars_error = dependent_vars_error[non_nan_rows]
    mask = numpy.concatenate((non_nan_rows,
                              numpy.ones(n_coeff, dtype=bool)))
    if args.error_method is not None:
        fit, fit_err = args.error_method(dependent_vars,
                                         independent_vars,
                                         dependent_vars_error,
                                         args.add_const,
                                         args.sigma_method, args.sigma,
                                         args.mean_modulus, args.units,
                                         args.rcond, args.sigma_max_iter,
                                         args.error_iterations,
                                         args.error_processes)
        data[args.distance_label      ] = fit
        data[args.distance_error_label] = fit_err
    else:
        fit = leavitt_law(dependent_vars, independent_vars,
                          dependent_vars_error,
                          args.add_const, args.fit_modulus,
                          args.sigma_method, args.sigma,
                          args.mean_modulus, args.units,
                          args.rcond, args.sigma_max_iter,
                          args.debug)
        data.loc[mask, args.distance_label] = fit

    data.to_csv(stdout, sep=args.output_sep, float_format=args.format,
                na_rep=args.output_na_value)

    return 0

if __name__ == "__main__":
    exit(main())
