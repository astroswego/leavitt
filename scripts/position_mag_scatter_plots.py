from sys import argv, stdin, stderr

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

usage_string = """\
Usage: radec_contour_plots.py ([output file] ...)

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
        ax = fig.add_subplot(111, axis_bgcolor='black',
                             aspect='equal', adjustable='datalim')

        sc = ax.scatter(RA, DEC, c=band_data,
                        marker=',', s=5, edgecolors='none',
                        cmap=mpl.cm.Blues)

        ax.set_xlabel(r"Right Ascension (degrees)")
        ax.set_ylabel(r"Declination (degrees)")

        cbar = fig.colorbar(sc)
        cbar.set_label("Apparent Magnitude")

        fig.savefig(output_prefix + band_name + "." + output_extension)
        plt.close(fig)
    return 0

if __name__ == "__main__":
    validate_args()
    exit(main(*argv[1:]))
