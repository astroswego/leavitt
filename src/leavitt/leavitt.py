from argparse import ArgumentError, ArgumentParser, FileType, SUPPRESS
from sys import exit, stdin, stderr
from os import path
import numpy
from sklearn.linear_model import LinearRegression

from leavitt.regression import SVD

regressor_choices = {
    "QR": LinearRegression(fit_intercept=True),
    "SVD": SVD()
}

def get_args():
    parser = ArgumentParser(prog="leavitt")

    general_group    = parser.add_argument_group("General")
    output_group     = parser.add_argument_group("Optional Output")
    regression_group = parser.add_argument_group("Regression")
    outlier_group    = parser.add_argument_group("Outlier Detection")

    ## General Options ##
    general_group.add_argument("-i", "--input", type=str,
        default=stdin.buffer,
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
    regression_group.add_argument("-m", "--method", type=str,
        default="svd", choices=["svd", "qr"],
        help="Method used for solving least-squares matrix "
             "(default = svd)")

    ## Outlier Options ##
    outlier_group.add_argument("--sigma", type=float,
        default=numpy.PINF,
        help="rejection criterion for outliers "
             "(default = infinity)")
    outlier_group.add_argument("--sigma-metric", type=str,
        default="standard", choices=["standard", "robust"],
        help="sigma clipping method to use "
             "(default = standard)")

    args = parser.parse_args()

    

    return args

def main(args=None):
    if args is None:
        args = get_args()

    
    

    return 0

if __name__ == "__main__":
    exit(main())
