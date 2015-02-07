import numpy
from leavitt.utils import identity, zscore

from sys import stdout, stderr

__all__ = [
    "design_matrix",
    "leavitt_law"
]

def simple_design_matrix(independent_vars, add_const, n_dependent_vars):
    n_samples = independent_vars.shape[0]

    if add_const:
        constants = numpy.ones((n_samples, 1))
        independent_vars = numpy.hstack((independent_vars, constants))

    n_samples, n_independent_vars = independent_vars.shape
    design_matrix = numpy.zeros((n_dependent_vars*n_samples,
                                 n_dependent_vars*n_independent_vars),
                                dtype=float)

    for i in range(n_dependent_vars):
        design_matrix[
            i*n_samples : (i+1)*n_samples,
            i*n_independent_vars : (i+1)*n_independent_vars
        ] = independent_vars

    return design_matrix

def design_matrix(dependent_vars, independent_vars, add_const=False):
    if add_const:
        independent_vars = numpy.hstack((independent_vars,
                                         numpy.ones((independent_vars.shape[0],
                                                     1))))
    n_samples, n_dependent = dependent_vars.shape
    n_samples, n_independent = independent_vars.shape
    design_matrix = numpy.zeros((n_samples*n_dependent,
                                 n_dependent*n_independent + n_samples),
                                dtype=float)
    diagonal = numpy.eye(n_samples)

    for i in range(n_dependent):
        design_matrix[
            i*n_samples : (i+1)*n_samples,
            n_samples + i*n_independent : n_samples + (i+1)*n_independent
        ] = independent_vars

        design_matrix[i*n_samples : (i+1)*n_samples, :n_samples] = diagonal

    return design_matrix, numpy.reshape(dependent_vars, -1)


def simple_leavitt_law(dependent_vars, independent_vars, add_const, rcond,
                       debug=False):
    n_samples, n_vars = dependent_vars.shape

    X = simple_design_matrix(independent_vars, add_const, n_vars)
    y = numpy.reshape(dependent_vars, -1)

    if debug:
        _print_debug(X, y)

    b, residuals, rank, s = numpy.linalg.lstsq(X, y, rcond=rcond)

    n_coeff = b.size

    fit = numpy.empty(n_samples+n_coeff, dtype=float)
    fit[:-n_coeff] = numpy.nan
    fit[-n_coeff:] = b

    return fit




def leavitt_law(dependent_vars, independent_vars, add_const=False,
                fit_modulus=False,
                sigma_method=zscore, sigma=0.0,
                mean_modulus=0.0, unit_conversion=identity,
                rcond=1e-3, max_iter=20,
                debug=False):
    n_samples, n_vars = dependent_vars.shape
    n_coeff = (1+add_const)*n_vars

    # if not fitting modulus, do simple PL fit
    if not fit_modulus:
        return simple_leavitt_law(dependent_vars, independent_vars,
                                  add_const, rcond, debug)
    # if sigma is 0 or less, do not perform any outlier detection
    if sigma <= 0:
        X, y = design_matrix(dependent_vars, independent_vars, add_const)
        if debug:
            _print_debug(X, y)
        # solve ``X*b = y`` for ``b``
        b, residuals, rank, s = numpy.linalg.lstsq(X, y, rcond=rcond)
        d = unit_conversion(b[:-n_coeff]+mean_modulus)
        return numpy.concatenate((d, b[-n_coeff:]))

    if max_iter < 1:
        raise Exception("At least one iteration required.")

    # initialize mask to all True
    mask = numpy.ones(n_samples, dtype=bool)

    for i in range(max_iter):
        X, y = design_matrix(dependent_vars[mask], independent_vars[mask],
                             add_const)
        if debug:
            _print_debug(x, y)
        # solve ``X*b = y`` for ``b``
        b, residuals, rank, s = numpy.linalg.lstsq(X, y, rcond=rcond)
        # extract distances from ``b`` and convert units
        dist = unit_conversion(b[:-n_coeff]+mean_modulus)
        new_mask = abs(sigma_method(dist)) < sigma
        if numpy.array_equal(mask[mask], new_mask):
            # no new outliers detected
            # terminate sigma clipping and return vector of coefficients,
            # which includes both distances and PL coefficients
            return _format_fit(dist, b[-n_coeff:], mask, n_samples, n_coeff)
        else:
            # new outliers detected, mask them and continue sigma clipping
            mask[mask] = new_mask
            continue
    # reached max iterations
    return _format_fit(dist[new_mask], b[-n_coeff:], mask, n_samples, n_coeff)


def _format_fit(dist, coeffs, mask, n_samples, n_coeff):
    fit = numpy.empty(n_samples+n_coeff, dtype=float)

    fit[:-n_coeff][ mask] = dist
    fit[:-n_coeff][~mask] = numpy.nan
    fit[-n_coeff:]        = coeffs

    return fit

def _print_debug(X, y):
    n_rows, n_cols = X.shape
    out = numpy.empty((n_rows, n_cols+2), dtype=float)
    out[:n_rows, :n_cols] = X
    out[:n_rows, n_cols] = numpy.nan
    out[:n_rows, -1] = y
    print("X, y =", file=stderr)
    numpy.savetxt(stderr.buffer, out, fmt="%.5f")
