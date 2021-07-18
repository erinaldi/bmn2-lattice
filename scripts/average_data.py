import numpy as np
import pandas as pd
from emcee import autocorr

Ts = ["04", "035", "03", "025", "02", "015", "01", "005", "0025"]#, "001"]
Ls = ["16", "24", "32", "48", "64", "96", "128", "192"]
cut = 1000 # thermalization cut in units of MDTU
N = 3
G = "05"
datarun = f"../lattice/improv_runs/bmn2_su{N}_g{G}"
# header
header = f"T,L,E,err,meas,freq,tau"
with open(f"{datarun}/e.csv","w") as f:
    print(header,file=f)
    for L in Ls:
        for T in Ts:
            filename = f"{datarun}/l{L}/t{T}/data.h5"
            try:
                data = pd.read_hdf(filename, "mcmc_obs")
                data.e = data.e * float(N) ** 2
                df = data.query("mdtu > @cut")
                avg, std = df.e.mean(), df.e.std()
                bins = df.shape[0]
                # select only one saving frequency, the last one
                freqs = df.freq.dropna().unique()
                freq = freqs[-1]
                energy = df.query("freq == @freq").e
                tau = autocorr.integrated_time(energy.values, tol=0)
                print(f"0.{T[1:]},{L},{avg:.4f},{std/np.sqrt(bins):.4f},{int(bins)},{int(freq)},{tau[0]:.2f}", file=f)
            except (ValueError, FileNotFoundError) as e:
                pass