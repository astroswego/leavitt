from functools import reduce
from multiprocessing import Pool
import numpy

__all__ = [
    "any_nan",
    "char",
    "colvec",
    "identity",
    "modulii2pc",
    "modulii2kpc",
    "pmap",
    "zscore"
]


def any_nan(*args, axis=0):
    return reduce(numpy.logical_or,
                  map(numpy.isnan, args)).any(axis=axis)


def char(x):
    if isinstance(x, str) and len(x) == 1:
        return x
    else:
        raise ValueError("Must be a single character string: {}".format(x))


def colvec(X):
    return numpy.reshape(X, (-1, 1))


def identity(x):
    return x

def modulii2pc(modulii):
    return 10**(modulii/5 + 1)


def modulii2kpc(modulii):
    return 10**(modulii/5 + 1) / 1000


def pass_fn(*args, **kwargs):
    pass


def pmap(func, args, processes=None, callback=pass_fn, **kwargs):
    """Parallel equivalent of map(func, args), with the additional ability of
    providing keyword arguments to func, and a callback function which is
    applied to each element in the returned list. Unlike map, the output is a
    non-lazy list. If processes=1, no thread pool is used.
    """
    if processes is 1:
        results = []
        for arg in args:
            result = func(arg, **kwargs)
            results.append(result)
            callback(result)
        return results
    else:
        with Pool() if processes is None else Pool(processes) as p:
            results = [p.apply_async(func, (arg,), kwargs, callback)
                       for arg in args]

            return [result.get() for result in results]


def repeatedly(fn, N):
    return (fn() for _ in range(N))

def zscore(X):
    return (X - numpy.mean(X)) / numpy.std(X)
