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
    return (X - X.mean()) / X.std()
