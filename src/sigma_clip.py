from argparse import ArgumentParser
import numpy as np

def get_args():
    parser = ArgumentParser(
        prog="sigma_clip",
        description="Computes z-scores of elements in eval file, "
                    "and prints corresponding lines of output file.")

    parser.add_argument("eval file", type=str,
        help="Name of eval file, which is used to flag outliers.")
    parser.add_argument("output file", type=str,
        help="Name of output file, whose rows are selected by eval file")
    parser.add_argument("-s", "--sigma", type=float, default=3.0,
        help="Cutoff z-score")
    parser.add_argument("--show-z-score",
        action="store_true", default=False,
        help="Display z-scores of selected elements")

    args = parser.parse_args()

    return args

def z_score(mean, std):
    return lambda x: (mean - x) / std

def main():
    args = vars(get_args())

    sigma = args["sigma"]
    show_z_score = args["show_z_score"]
    eval_data = np.loadtxt(args["eval file"])

    mean, std = np.mean(eval_data), np.std(eval_data)

    with open(args["output file"], "r") as output_file:
        for line, z in zip(output_file,
                           map(z_score(mean, std), eval_data)):
            if abs(z) < sigma:
                if show_z_score:
                    print(z, end="\t")
                print(line, end="")

    return 0

if __name__ == "__main__":
    exit(main())
