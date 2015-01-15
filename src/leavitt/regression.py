from functools import reduce
from itertools import chain, repeat
import numpy

from leavitt.utils import colvec, zscore

__all__ = [
    "distance_formula"
]

def _make_tile(independent_vars, add_const):
    if add_const:
        n_rows, n_cols = independent_vars.shape
        return numpy.hstack((independent_vars, numpy.ones((n_rows,1))))
    else:
        return independent_vars

def _make_row(index, tile, identity, zeros, n_vars):
    diagonals = [identity]
    front_zeros = repeat(zeros, index)
    element = [tile]
    end_zeros = repeat(zeros, n_vars-index-1)
    column_blocks = tuple(chain(diagonals,
                                front_zeros,
                                element,
                                end_zeros))

    return numpy.hstack(column_blocks)

def distance_formula(dependent_vars, independent_vars, add_const=False):
    tile = _make_tile(independent_vars, add_const)
    n_samples, n_independent = tile.shape
    n_samples, n_dependent = dependent_vars.shape
    
    identity = numpy.eye(n_samples)
    zeros = numpy.zeros((n_samples, n_independent))


    make_row = lambda i: _make_row(i, tile, identity, zeros, n_independent)

    for i in range(n_dependent):
        print(make_row(i).shape)

    # crashing here because the rows are different sizes for some reason
    # prints above show this
    design_matrix = numpy.vstack(tuple(make_row(i)
                                       for i in range(n_dependent)))
#    rows = tuple(map(make_row, range(len(dependent_vars))))
    
#    independent_vars = numpy.vstack(rows)

    return design_matrix, dependent_vars


def fit_with_sigma_clip(dependent_vars, independent_vars, add_const=False,
                        sigma_method=zscore, sigma=0.0,
                        mean_modulus=0.0, units="modulii", max_iter=20):
    # if sigma is 0 or less, do not perform any outlier detection
    if sigma <= 0:
        X, y = distance_formula(dependent_vars[mask], independent_vars[mask],
                                add_const)
        # solve ``X*b = y`` for ``b``
        b, residuals, rank, s = numpy.linalg.lstsq(X, y)
        d = convert_units(b[:-n_coeff], units)
        return numpy.concatenate((d, b[-n_coeff:]))
        
    if max_iter < 1:
        raise Exception("At least one iteration required.")

    n_samples, n_vars = independent_vars.shape
    n_coeff = (1+add_const)*n_vars
    # initialize mask to all True
    mask = numpy.ones(n_samples, dtype=bool)

    for i in range(max_iter):
        X, y = distance_formula(dependent_vars[mask], independent_vars[mask],
                                add_const)
        # solve ``X*b = y`` for ``b``
        b, residuals, rank, s = numpy.linalg.lstsq(X, y)
        # extract distances from ``b`` and convert units
        dist = convert_units(b[:-n_coeff], units)
        new_mask = sigma_method(dist) < sigma
        if mask[mask] == new_mask:
            # no new outliers detected
            # terminate sigma clipping and return vector of coefficients,
            # which includes both distances and PL coefficients
            return numpy.concatenate((dist, b[-n_coeff:]))
        else:
            # new outliers detected, mask them and continue sigma clipping
            mask[mask] = new_mask
            continue

    return b

def lstsq(*args, **kwargs):
    x, residuals, rank, s = numpy.linalg.lstsq(*args, **kwargs)

    return x
