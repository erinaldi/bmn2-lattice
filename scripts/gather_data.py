# this script will create the h5 files for each lattice parameter set
# given N, g, m, T we collect all the observables along the monte carlo trajectory
# including the parameters of the monte carlo integration
# %%
import numpy as np
from glob import glob
import h5py as h5
from pathlib import Path
from linecache import getline
import re

# %%
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
    pattern = r"(\d\.?\d+)\s+"
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


# %%
Path.glob()
# Util to travers h5 files tree and print name for groups and datasets
# using the `visit` method
def printname(name):
    print(name)

# %%
# Choose the data folder
folders = np.array(glob("../improv_runs/bmn2_su2_g20/l64/t04/*.txt"))[::-1]
n, l, m = get_params(folders[0])[:-1]

# %%
# Open the HDF5 file
f = h5.File("correlator.h5")
# Create group for the corresponding data folder
g = f.create_group("nf={}_L={}_mf={}".format(n, l, m))

# Choose how many distances to keep.
Nd = 100

# Create groups for all flow times
for jobfolder in folders:
    flowTime = get_params(jobfolder)[3]
    g.create_group("tw={}".format(flowTime))
    # Collect the actual data into numpy arrays and place it into datasets in the corresponding h5 file groups
    cfgfiles = np.array(glob(jobfolder + "/Data/data_corr.*.txt"))
    distance, testcorr = np.loadtxt(np.sort(cfgfiles)[0], usecols={0, 1}, unpack=True)
    for cfgfile in np.sort(cfgfiles)[1:]:
        testcorr = np.vstack((testcorr, np.loadtxt(cfgfile, usecols={1}, unpack=True)))
    distance = distance[:Nd]
    testcorr = testcorr[:, :Nd]
    g["tw={}".format(flowTime)].create_dataset("correlator", data=testcorr)
    g["tw={}".format(flowTime)].create_dataset("distance", data=distance)
# close
f.close()
