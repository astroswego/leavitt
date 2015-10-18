import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic_2d

from sys import argv

def main(ra_filename, dec_filename, residual_filename,
         output_prefix, ext, *bands):
    ra = np.loadtxt(ra_filename)
    dec = np.loadtxt(dec_filename)

    residuals = np.loadtxt(residual_filename, unpack=True)

    for band, res in zip(bands, residuals):
        fig = plt.figure()
        ax = fig.add_subplot(111,
                             aspect='equal', adjustable='box')

        resid_grid, ra_bin, dec_bin, _ = binned_statistic_2d(ra, dec, res,
                                                             bins=20,
                                                             statistic=np.std)
        ra_grid, dec_grid = np.meshgrid(ra_bin[:-1], dec_bin[:-1])

        cn = ax.contourf(ra_grid, dec_grid, resid_grid, 20)

        ax.set_xlabel(r"Right Ascension (degrees)")
        ax.set_ylabel(r"Declination (degrees)")

        ax.locator_params(axis="x", tight=True, nbins=5)

        cbar = fig.colorbar(cn)
        cbar.set_label("Depth (mag std)")

        fig.savefig("{}{}.{}".format(output_prefix, band, ext))
        plt.close(fig)


if __name__ == "__main__":
    exit(main(*argv[1:]))
