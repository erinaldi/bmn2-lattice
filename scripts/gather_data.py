# this script will create the h5 files for each lattice parameter set
# given N, g, m, T we collect all the observables along the monte carlo trajectory
# including the parameters of the monte carlo integration
# %%
import pandas as pd
from pathlib import Path
from linecache import getline
import re
import fire

# %%
# extract the MCMC parameters for a run (they are contained in the header)
# they will be used as new columns in the dataframe so we can plot them for each run
def get_params(pfile: str) -> dict:
    """Extract the parameters of a MC chain by looking at the header of the output file.txt

    Args:
        pfile (str): a MC output file passed as a string

    Returns:
        dict: the parameters of the MC run returned as a dictionary
    """
    pattern = r"[:=]\s+(\d.*)$"
    line_nmat = getline(pfile, 1)
    nmat = re.findall(pattern, line_nmat)[0]
    line_ntau = getline(pfile, 3)
    ntau = re.findall(pattern, line_ntau)[0]
    line_xdtau = getline(pfile, 4)
    xdtau = re.findall(pattern, line_xdtau)[0]
    line_udtau = getline(pfile, 5)
    udtau = re.findall(pattern, line_udtau)[0]
    line_more = getline(pfile, 2)
    more = re.findall(pattern, line_more)[0]
    pattern = r"[\d.]+(?:E-?\d+)?"
    t, m, g = re.findall(pattern, more)
    return {
        "nmat": int(nmat),
        "ntau": int(ntau),
        "xdtau": float(xdtau),
        "udtau": float(udtau),
        "temperature": float(t),
        "mass": float(m),
        "coupling": float(g),
    }


# Explaining the regexp for the final 3 numbers (from https://stackoverflow.com/questions/4479408/regex-for-numbers-on-scientific-notation)
# -?      # an optional -
# [\d.]+  # a series of digits or dots (see *1)
# (?:     # start non capturing group
#   E     # "E"
#   -?    # an optional -
#   \d+   # digits
# )?      # end non-capturing group, make optional
# %%
# read the observables from a txt file and create a dataframe
# also add the MCMC params as new columns, using the trajectory number as index
def create_dataframe(pfile: str) -> pd.DataFrame:
    """Create the dataframe containing the observables for each trajectory.
    Then add the MCMC parameters from the header as additional columns.
    This is advantageous because these parameters can be used to group specific trajectories together.

    Args:
        pfile (str): The name of the txt file where the observables are saved

    Returns:
        pd.DataFrame: a `pandas` dataframe containing the observables and the MCMC parameters of the run

    """
    try:
        mc_params = get_params(pfile)
    except:
        print("Problem getting the mcmc parameters")
    # column names
    cols = ["tj", "dH", "e", "p", "x2", "f2", "ub", "acc"]
    # and their types
    typs = {
        "tj": int,
        "dH": float,
        "e": float,
        "p": float,
        "x2": float,
        "f2": float,
        "ub": float,
        "acc": float,
    }
    # read data: skip header, make tj the index
    data = pd.read_csv(
        pfile, sep="\s+", skiprows=7, names=cols, dtype=typs, index_col="tj"
    )
    # add mcmc params as columns
    for k, v in mc_params.items():
        data[k] = v
    # add traj_length and mdtu and save frequency columns
    data["tau"] = data.xdtau * data.ntau
    data["mdtu"] = data.tau * data.index
    data["freq"] = data.mdtu.diff()
    return data


# %%
# main function to gather the data from a folder or many folders
def gather_data(
    data_folder: str = "../lattice/improv_runs",
    run_folder: str = "bmn2_su3_g20/l128/t005",
    do_all: bool = False,
):
    """Collect all the data for the observables in different output files for the same set of parameters

    Args:
        data_folder (str, optional): The main data folder where all the different parameters were run. Defaults to "../../lattice/improv_runs/".
        run_folder (str, optional): The specific run folder with gauge group, coupling, lattice size and temperature. Defaults to "bmn2_su3_g20/l128/t005".
        do_all (bool, optional): If we should collect the data from all runs or just the one specified. Defaults to False.
    """
    pdata = Path(data_folder)
    assert pdata.is_dir()
    assert (pdata / run_folder).is_dir()
    if do_all:
        all_runs = [x for x in pdata.glob("bmn2_*/l*/t*")]
    else:
        all_runs = [pdata / run_folder]
    # loop over runs: they are Path objects
    print(f"We have a total of {len(all_runs)} runs to gather...")
    for run in all_runs:
        # get the output files: should end with a number before the extension
        pfiles = [x for x in run.glob("*[0-9].txt") if x.is_file()]
        if len(pfiles) > 0:
            print(f"- We have a total of {len(pfiles)} files in run {run}")
            frames = [create_dataframe(str(f)) for f in pfiles]
            result = pd.concat(frames, verify_integrity=True)
            print(f"-- total data size: {result.shape}")
            outputfile = run / "data.h5"
            result.sort_index().to_hdf(outputfile, "mcmc_obs", format="fixed", mode="w")
            print(f"-- file saved in {outputfile.as_posix()}")


if __name__ == "__main__":
    fire.Fire(gather_data)
