import numpy as np
from sys import argv, stdout, stderr

def main(logP_filename, mag_filename):
    logP = np.loadtxt(logP_filename)
    mag = np.loadtxt(mag_filename)

    A = np.column_stack((logP, np.ones_like(logP)))

    x, residuals, rank, s = np.linalg.lstsq(A, mag)

    np.savetxt(stdout.buffer, x)
#    np.savetxt(residual_filename, residuals)

if __name__ == "__main__":
    exit(main(*argv[1:]))
