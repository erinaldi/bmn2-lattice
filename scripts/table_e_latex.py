# create tabular latex text from csv file of energies
import pandas as pd
from tabulate import tabulate
import gvar as gv
import os, sys, argparse


def gvarfromrow(row):
    """Generate a gvar class from the elements of a dataframe rows

    Args:
        row (pandas.DataFrame): a row from df.iterrows() for example:

    Returns:
        gvar.gvar: a gvar object with mean and standard deviation (useful for pretty printing and fitting)
    """
    return gv.gvar(row.E, row.err)


def parsing_args():
    parser = argparse.ArgumentParser(
        description="Write tabulated data in LaTeX format on screen for the Energy"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="../lattice/improv_runs/bmn2_su2_g05/e.csv",
        help="change default name of CSV file. (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="tables",
        help="change default folder for saving TEX table. (default: %(default)s)",
    )
    args = parser.parse_args()
    print("Arguments passed")
    print(args)
    ########
    filename = args.file
    if not os.path.isfile(filename):
        print(f"CSV file {filename} does not exist. Exiting.")
        sys.exit()
    folder = args.output
    if not os.path.isdir(folder):
        print(f"Folder {folder} does not exist. Exiting.")
        sys.exit()


    return filename, folder


if __name__ == "__main__":
    filename, outfolder = parsing_args()
    data = pd.read_csv(filename)

    # make new column
    data["egv"] = data.apply(gvarfromrow, axis=1)

    # print out table with header line
    outfilename = filename.split("/")[-2]
    outfile = f"{outfolder}/{outfilename}_e.tex"
    print(f"Saving to {outfile}")
    with open(outfile,"w") as f:
        print(
            tabulate(
                data[["T", "L", "egv", "meas", "freq", "tau"]].values,
                headers=["$T$", "$n_t$", "E", "$N_\\textrm{cfgs}$", "$N_\\textrm{drop}$", "$\\tau$"],
                floatfmt=".3f",
                tablefmt="latex_raw",
            ), file=f
        )
