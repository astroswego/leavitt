import numpy

from leavitt.regression import leavitt_law
from leavitt.utils import identity, pmap, repeatedly, zscore

__all__ = [
    "apply_monte_carlo",
    "monte_carlo"
]

def apply_monte_carlo(X, dX, loc=0.0, scale=1.0):
    mc = numpy.random.normal(loc=loc, scale=scale, size=dX.shape)
    return X + dX*mc

def monte_carlo(dependent_vars, independent_vars, dependent_vars_error,
                add_const=False, sigma_method=zscore, sigma=0.0,
                mean_modulus=0.0, unit_conversion=identity,
                rcond=1e-3, max_iter=20, iterations=100, processes=1):
    n_samples, n_vars = dependent_vars.shape
    n_coeff = (1+add_const)*n_vars

    # make the initial fit without error, in order to mark outliers
    initial_fit = leavitt_law(dependent_vars, independent_vars, add_const,
                              True,
                              sigma_method, sigma,
                              mean_modulus, unit_conversion,
                              rcond, max_iter)
    coefficients = initial_fit[-n_coeff:]

    if sigma > 0.0:
        # mask marks inliers as True, and outliers as False
        mask = ~numpy.isnan(initial_fit[:-n_coeff])
    else:
        # no outlier detection requested, therefore mask includes all samples
        mask = numpy.ones(n_samples, dtype=bool)

    mc_dependent_vars = repeatedly(
        lambda: apply_monte_carlo(dependent_vars[mask],
                                  dependent_vars_error[mask]),
        iterations)
    mc_fits = pmap(leavitt_law, mc_dependent_vars, processes=processes,
                   independent_vars=independent_vars[mask], add_const=add_const,
                   fit_modulus=True,
                   mean_modulus=mean_modulus, unit_conversion=unit_conversion,
                   rcond=rcond, max_iter=max_iter)

    dist = numpy.empty(n_samples+n_coeff, dtype=float)
    err = numpy.empty(n_samples+n_coeff, dtype=float)

    dist[:-n_coeff][ mask] = numpy.mean(mc_fits, axis=0)[:-n_coeff]
    dist[:-n_coeff][~mask] = numpy.nan
    dist[-n_coeff:]        = coefficients
    err [:-n_coeff][ mask] = numpy.std(mc_fits, axis=0)[:-n_coeff]
    err [:-n_coeff][~mask] = numpy.nan

    return dist, err
