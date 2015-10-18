import numpy as np
from sys import argv, stdout, stderr

usage_string = """\
Usage: table_arith.py LHS OPERATION RHS

Reads two table files, and performs an arithmatic operation on them.

Operations are: + - * /

Tables must have same dimensions.

Writes resulting table to stdout.
"""

def print_usage():
    print(usage_string, file=stderr)
    exit(1)

def validate_args(argv):
    if len(argv) != 4:
        print_usage()

operations = {
    "+": np.add,
    "-": np.subtract,
    "*": np.multiply,
    "/": np.divide
}


def main(LHS_filename, operation, RHS_filename):
    LHS = np.loadtxt(LHS_filename)
    RHS = np.loadtxt(RHS_filename)

    try:
        operation = operations[operation]
    except KeyError:
        print_usage()

    output_data = operation(LHS, RHS)

    np.savetxt(stdout.buffer, output_data)


if __name__ == "__main__":
    validate_args(argv)
    exit(main(*argv[1:]))
