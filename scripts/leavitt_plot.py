import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sys import argv


def fit_line(coeff, min_logP, max_logP):
    logP = np.arange(min_logP, max_logP, 0.01)
    ones = np.ones_like(logP)

    A = np.column_stack((logP, ones))

    mag = A.dot(coeff)

    return logP, mag


def plot(logP, mag, coeff, output_prefix, band, ext):
    logP_fit, mag_fit = fit_line(coeff, min(logP), max(logP))

    fig, ax = plt.subplots()

    ax.set_title(r"Leavitt Law in ${}$-band".format(band))

    ax.set_xlabel(r"$\log P$")
    ax.set_ylabel(r"$m$")

    ax.invert_yaxis()

    ax.scatter(logP, mag, marker=".", c="black")
    ax.plot(logP_fit, mag_fit, "r-")

    fig.savefig("{}{}.{}".format(output_prefix, band, ext))

    plt.close(fig)


def main(logP_filename, mags_filename, coeffs_filename, output_prefix, ext,
         *bands):
    logP = np.loadtxt(logP_filename)
    mags = np.loadtxt(mags_filename, unpack=True)
    coeffs = np.loadtxt(coeffs_filename, unpack=True)

    for band, mag, coeff in zip(bands, mags, coeffs):
        plot(logP, mag, coeff, output_prefix, band, ext)


if __name__ == "__main__":
    exit(main(*argv[1:]))
