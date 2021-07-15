# this script will create the h5 files for each lattice parameter set
# given N, g, m, T we collect all the observables along the monte carlo trajectory
# including the parameters of the monte carlo integration
# %%
import numpy as np
import pandas as pd
from pathlib import Path
from linecache import getline
import re

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
    # add mdtu columns
    data["mdtu"] = data.xdtau * data.ntau * data.index
    return data


# %% [markdown]
# Define the data folder and get the subfolders with the data files

# %%
# lattice data folder
data_lattice = "../../lattice/improv_runs/"
pdata = Path(data_lattice)
runs = [x for x in pdata.glob("bmn2_*/l*/t*")]
print(f"We have a total of {len(runs)} runs")
# %% [markdown]
# Get txt files inside a folder

# %%
pfiles = [x for x in runs[0].glob("*.txt") if x.is_file()]
print(f"All files: {pfiles}")

# %%
# Use list comprehension to create the final dataframe of a MCMC run
frames = [create_dataframe(str(f)) for f in pfiles]
result = pd.concat(frames)

# %%
# save to hdf5 binary format
result.to_hdf("test.h5", "mcmc_obs", format="fixed", mode="w")
# %%
