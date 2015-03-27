import numpy
import statsmodels.api as sm
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

    return design_matrix, numpy.transpose(dependent_vars).flatten()

def modulus_design_matrix(n_bands, n_samples):
    return numpy.tile(numpy.eye(n_samples),
                      (n_bands, 1))

def stack_vars(vars):
    return numpy.transpose(vars).flatten()

def simple_leavitt_law(dependent_vars, independent_vars, add_const, rcond,
                       debug=False):
    n_samples, n_vars = dependent_vars.shape

    X = simple_design_matrix(independent_vars, add_const, n_vars)
    y = stack_vars(dependent_vars)

    if debug:
        _print_debug(X, y)

    b, residuals, rank, s = numpy.linalg.lstsq(X, y, rcond=rcond)

    n_coeff = b.size

    fit = numpy.empty(n_samples+n_coeff, dtype=float)
    fit[:-n_coeff] = numpy.nan
    fit[-n_coeff:] = b

    return fit

def _err(intrinsic, photometric, slope, zero_point, logP):
    return numpy.sqrt(
        intrinsic**2 +
        photometric**2 +
        (slope*logP)**2 +
        zero_point**2
    )

def error_leavitt_law(intrinsic_error, photometric_error,
                      slope_error, zero_point_error,
                      logP):
    # print(photometric_error.shape,
    #       slope_error.shape,
    #       zero_point_error.shape,
    #       logP.shape,
    #       file=stderr)
    # exit()
    errors = numpy.empty_like(photometric_error)
    n_bands = slope_error.size

    for i in range(n_bands):
        errors[:,i] = _err(intrinsic_error,
                           photometric_error[:,i],
                           slope_error[i], zero_point_error[i],
                           logP[:,0])
    return errors

def leavitt_law(dependent_vars, independent_vars,
                dependent_vars_error,
                add_const=False, fit_modulus=False,
                sigma_method=zscore, sigma=0.0,
                mean_modulus=0.0, unit_conversion=identity,
                rcond=1e-3, max_iter=20,
                intrinsic_error=0.05,
                debug=False):
    n_samples, n_vars = dependent_vars.shape
    n_coeff = (1+add_const)*n_vars

    # if not fitting modulus, do simple PL fit
    if not fit_modulus:
        return simple_leavitt_law(dependent_vars, independent_vars,
                                  add_const, rcond, debug)
    # if sigma is 0 or less, do not perform any outlier detection
    if sigma <= 0:
        X_pl = simple_design_matrix(independent_vars, add_const, n_vars)
        y    = stack_vars(dependent_vars)
        model_pl = sm.OLS(y, X_pl)
        results_pl = model_pl.fit()
        coeffs_pl = results_pl.params

        stderr_pl = results_pl.HC0_se
        slope_err      = stderr_pl[0::2]
        zero_point_err = stderr_pl[1::2]
        error = stack_vars(error_leavitt_law(intrinsic_error,
                                             dependent_vars_error,
                                             slope_err, zero_point_err,
                                             independent_vars))
#        pl_coeffs, pl_residuals, pl_rank, pl_sv = numpy.linalg.lstsq(X_pl, y)

        fitted_y = results_pl.fittedvalues
        residuals = y - fitted_y

        X_modulus = modulus_design_matrix(n_vars, n_samples)
        model_modulus = sm.WLS(residuals, X_modulus, error)
        results_modulus = model_modulus.fit()
        coeffs_modulus = results_modulus.params
        
        dist = unit_conversion(coeffs_modulus + mean_modulus)
        ret = numpy.concatenate((dist, coeffs_pl))
        if debug:
            print(ret, file=stderr)
        return ret

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
