import numpy as np
from sys import argv, stdout, stderr

def main(logP_filename, pl_coeffs_filename):
    logP = np.loadtxt(logP_filename)
    b = np.loadtxt(pl_coeffs_filename)

    A = np.column_stack((logP, np.ones_like(logP)))

    mag = A.dot(b)

    np.savetxt(stdout.buffer, mag)

if __name__ == "__main__":
    exit(main(*argv[1:]))
