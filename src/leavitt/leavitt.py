from argparse import ArgumentError, ArgumentParser, FileType, SUPPRESS
from sys import exit, stdin, stdout, stderr
from os import path
import numpy
import pandas
from pandas import DataFrame
from pandas.io.parsers import read_table
from itertools import chain, count, product
from leavitt.regression import fit_with_sigma_clip
from leavitt.error import monte_carlo
from leavitt.utils import char, zscore

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
    

def get_args():
    parser = ArgumentParser(prog="leavitt")

    general_group    = parser.add_argument_group("General")
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
        default=False,
        help="Add a constant term to each equation")
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

    args = parser.parse_args()

    args.error_method = error_choices[args.error_method]
    if args.error_method is not None \
       and args.error_prefix == args.error_suffix == "":
            raise ArgumentError("An error prefix or suffix must be provided "
                                "for error to be computed")

    args.sigma_method = sigma_choices[args.sigma_method]

    return args

def main(args=None):
    if args is None:
        args = get_args()

    data = read_table(args.input, index_col=0, sep=args.sep,
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

    if args.error_method is not None:
        try:
            independent_vars_error = data[
                [args.error_prefix + var + args.error_suffix
                 for var in args.independent_vars]
            ].iloc[:-n_coeff].values
        except KeyError as e:
            key = e.args[0]
            print("Missing entry in input table for error: {}".format(key),
                  file=stderr)
            return 1

        fit, fit_err = args.error_method(dependent_vars,
                                         independent_vars,
                                         independent_vars_error,
                                         args.add_const,
                                         args.sigma_method, args.sigma,
                                         args.mean_modulus, args.units)
        data[args.distance_label] = fit
        data[args.error_prefix
           + args.distance_label
           + args.error_suffix] = fit_err
    else:
        fit = fit_with_sigma_clip(dependent_vars, independent_vars,
                                  args.add_const,
                                  args.sigma_method, args.sigma,
                                  args.mean_modulus, args.units,
                                  args.rcond, args.sigma_max_iter)
        data[args.distance_label] = fit

    data.to_csv(stdout, sep=args.output_sep, na_rep="NaN")

    return 0

    # Everything below is dead code
    # which I'm only keeping as a reference until the above code works right

        
    nrows, ncols = data.shape
    arg_coeff = numpy.arange(nrows-n_coeff, nrows)

    label = lambda i: (args.distance_label + "_{}").format(i)

    for i in count():
        selection = data.dropna()
        if i == 0:
            arg_selected = numpy.arange(data.shape[0])
        else:
            prev_dist = selection[label(i-1)].iloc[:-n_coeff]
            sigmas = abs(args.sigma_method(prev_dist))
#            print(sigmas)
            arg_selected = numpy.arange(nrows)[sigmas.values < args.sigma]
#            print(arg_selected); exit()

            n_selected = arg_selected.shape[0]
            n_prev     = prev_dist.dropna().shape[0]

            print("n_selected:n_prev = {}:{}".format(n_selected, n_prev),
                  file=stderr)
            # finished sigma clipping
            if n_selected == n_prev:
                data[args.distance_label] = data[label(i-1)]
                break

#            print("shape before:", arg_selected.shape, file=stderr)
#            print("A:", arg_selected, file=stderr)
#            exit()

            selection = selection.iloc[arg_selected]
            arg_selected = numpy.concatenate([arg_selected, arg_coeff])

#            print("shape after:", arg_selected.shape, file=stderr)
            
        y, A = distance_formula(selection,
                                args.dependent_vars, args.independent_vars,
                                args.add_const)
        x = lstsq(A, y, rcond=args.rcond)
        x[:-n_coeff] = convert_units(x[:-n_coeff]+args.mean_modulus,
                                     args.units)
        # restrict this to the args != NaN, except for the coeffs
        data[label(i)] = numpy.nan
#        print(data[label(i)].iloc[arg_selected]); exit()
        data[label(i)].iloc[arg_selected] = x
#        data[label(i)].loc[-n_coeff:] = x[-n_coeff:]


    """

    
    y, A = distance_formula(data.dropna(),
                            args.dependent_vars, args.independent_vars,
                            args.add_const)

#    x = numpy.linalg.lstsq(A, y, rcond=1)[0]
    x = args.regressor(A, y, rcond=1e-3)
    x[:-n_coeff] = convert_units(x[:-n_coeff]+args.mean_modulus, args.units)
    data["dist_0"] = x

    for iteration in count(start=1):
        prev_label = "dist_{}".format(iteration-1)
        prev_selected = data.dropna()
#        prev_selected = data.loc[~numpy.isnan(data[prev_label])]
        arg_selected = (args.sigma_method(prev_selected[prev_label].values)
                        < args.sigma)#.flatten()
        next_selected = prev_selected.loc[arg_selected]

        # finished sigma clipping
        if prev_selected.shape == next_selected.shape:
            break

        next_label = "dist_{}".format(iteration)
        y, A = distance_formula(next_selected,
                                args.dependent_vars, args.independent_vars,
                                args.add_const)
#        x = numpy.linalg.lstsq(A, y, rcond=1)[0]
        x = args.regressor(A, y)
        x[:-n_coeff] = convert_units(x[:-n_coeff]+args.mean_modulus, args.units)

        data[next_label][arg_selected] = x

    """

    data.to_csv(stdout, sep=args.output_sep, na_rep="NaN")

    return 0

if __name__ == "__main__":
    exit(main())
