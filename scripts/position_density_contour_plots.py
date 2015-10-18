from sys import argv, stdin, stderr

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic_2d

usage_string = """\
Usage: position_mag_count_contour_plots.py [output prefix] [output extension]
                                           ([band] ...)

Reads whitespace-delimited text from stdin with columns:

  RA DEC band1 band2 ... bandN

There must be an equal number of bands and output files.
"""

def print_usage():
    print(usage_string, file=stderr)
    exit(1)

def validate_args():
    if len(argv) < 3:
        print_usage()

def validate_columns(data, band_names):
    if data.shape[0] != len(band_names)+2:
        print_usage()

def main(output_prefix, output_extension, *band_names):
    data = np.loadtxt(stdin.buffer, unpack=True)
    validate_columns(data, band_names)

    RA, DEC = data[:2]

    for band_data, band_name in zip(data[2:], band_names):
        fig = plt.figure()
        ax = fig.add_subplot(111,
                             aspect='equal', adjustable='box')

        # count the number of stars in each bin
        MAGii, RAi, DECi, _ = binned_statistic_2d(RA, DEC, band_data,
                                                  bins=20,
                                                  statistic='count')

        RAii, DECii = np.meshgrid(RAi[:-1], DECi[:-1])

        cn = ax.contourf(RAii, DECii, MAGii, 20)

        ax.set_xlabel(r"Right Ascension (degrees)")
        ax.set_ylabel(r"Declination (degrees)")

        ax.locator_params(axis="x", tight=True, nbins=5)

        cbar = fig.colorbar(cn)
        cbar.set_label("Star Count")

        fig.savefig(output_prefix + band_name + "." + output_extension)
        plt.close(fig)

if __name__ == "__main__":
    validate_args()
    exit(main(*argv[1:]))
