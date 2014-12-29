import numpy

def char(x):
    if isinstance(x, str) and len(x) == 1:
        return x
    else:
        raise Exception("Must be a single character string: {}".format(x))

def convert_units(modulii, units):
    """Converts units from modulii to parsecs and kiloparsecs"""
    if units == "modulii":
        return modulii
    elif units == "pc":
        return 10**(modulii/5 + 1)
    elif units == "kpc":
        return 10**(modulii/5 + 1) / 1000
    else:
        raise NotImplementedError

def zscore(X):
    return (X - numpy.nanmean(X)) / numpy.nanstd(X)

def colvec(X):
    return numpy.reshape(X, (-1, 1))
