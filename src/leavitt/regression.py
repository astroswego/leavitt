from functools import reduce
from itertools import chain, repeat
import numpy

from leavitt.utils import colvec

__all__ = [
    "distance_formula"
]

def _make_tile(frame, independent_vars, add_const, N):
    cols = [colvec(frame[var].dropna()) for var in independent_vars]
    if add_const:
        cols.append(numpy.ones((N,1)))
    return numpy.hstack(cols)

def _make_row(index, tile, identity, zeros, rows, cols, varcount):
    diagonals = [identity]
    front_zeros = repeat(zeros, index)
    element = [tile]
    end_zeros = repeat(zeros, varcount-index-1)
    column_blocks = tuple(chain(diagonals,
                                front_zeros,
                                element,
                                end_zeros))

    return numpy.hstack(column_blocks)

def distance_formula(frame, dependent_vars, independent_vars, add_const=False):
    rows, _ = frame.dropna().shape
    tile = _make_tile(frame, independent_vars, add_const, rows)
    _, cols = tile.shape
    identity = numpy.eye(rows)
    zeros = numpy.zeros((rows,cols))

    make_row = lambda i: _make_row(i,
                                   tile, identity, zeros,
                                   rows, cols, len(dependent_vars))

    rows = tuple(map(make_row, range(len(dependent_vars))))

    stacked_rows = numpy.vstack(rows)
    stacked_dependent_vars = numpy.concatenate(tuple(frame[var].dropna()
                                                     for var in dependent_vars))

    return stacked_dependent_vars, stacked_rows

def svd(A, b, debug=True):
    """Solves for x in `A x = b` using SVD."""
    U, s, V = numpy.linalg.svd(A, full_matrices=False)
    print("U:", U.shape)
    print("s:", s.shape)
    print("V:", V.shape)

    c = numpy.dot(U.T, b)
    print("c:", c.shape)
    w = numpy.linalg.solve(numpy.diag(s), c)
    print("w:", w.shape)

    return numpy.dot(V.T, w)

def lstsq(*args, **kwargs):
    x, residuals, rank, s = numpy.linalg.lstsq(*args, **kwargs)
    return x
