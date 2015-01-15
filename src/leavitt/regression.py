from functools import reduce
from itertools import chain, repeat
import numpy

from leavitt.utils import colvec, convert_units, zscore

__all__ = [
    "distance_formula"
]


def distance_formula(dependent_vars, independent_vars, add_const=False):
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


def fit_with_sigma_clip(dependent_vars, independent_vars, add_const=False,
                        sigma_method=zscore, sigma=0.0,
                        mean_modulus=0.0, units="modulii",
                        rcond=1e-3, max_iter=20):
    n_samples, n_vars = dependent_vars.shape
    n_coeff = (1+add_const)*n_vars
    # if sigma is 0 or less, do not perform any outlier detection
    if sigma <= 0:
        X, y = distance_formula(dependent_vars, independent_vars,
                                add_const)
        # solve ``X*b = y`` for ``b``
        b, residuals, rank, s = numpy.linalg.lstsq(X, y, rcond=rcond)
        d = convert_units(b[:-n_coeff]+mean_modulus, units)
        return numpy.concatenate((d, b[-n_coeff:]))

    if max_iter < 1:
        raise Exception("At least one iteration required.")

    # initialize mask to all True
    mask = numpy.ones(n_samples, dtype=bool)

    for i in range(max_iter):
        X, y = distance_formula(dependent_vars[mask], independent_vars[mask],
                                add_const)
        # solve ``X*b = y`` for ``b``
        b, residuals, rank, s = numpy.linalg.lstsq(X, y, rcond=rcond)
        # extract distances from ``b`` and convert units
        dist = convert_units(b[:-n_coeff]+mean_modulus, units)
        new_mask = abs(sigma_method(dist)) < sigma
        if numpy.array_equal(mask[mask], new_mask):
            # no new outliers detected
            # terminate sigma clipping and return vector of coefficients,
            # which includes both distances and PL coefficients
            return _format_fit(dist, b[-n_coeff:], mask, n_samples, n_coeff)
        else:
            # new outliers detected, mask them and continue sigma clipping
            print(mask.shape, new_mask.shape)
            mask[mask] = new_mask
            continue

    return _format_fit(dist[new_mask], b[-n_coeff:], mask, n_samples, n_coeff)


def _format_fit(dist, coeffs, mask, n_samples, n_coeff):
    fit = numpy.empty(n_samples+n_coeff, dtype=float)

    fit[:-n_coeff][ mask] = dist
    fit[:-n_coeff][~mask] = numpy.nan
    fit[-n_coeff:]        = coeffs

    return fit
