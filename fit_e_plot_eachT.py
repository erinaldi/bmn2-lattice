# fit and plot
import pandas as pd
from tabulate import tabulate
import gvar as gv
import lsqfit as ls
import numpy as np
import os, sys, argparse
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def make_data_eachT(data, Lcut=16):
    df = data.query("L > @Lcut")  # only sizes larger than Lcut
    x = df["1/L"].values
    y = df["E"].values
    yerr = df["err"].values
    return x, gv.gvar(y, yerr)


def fcn(x, p):  # order determined by size of p[a]
    c = p["a"]  # array of coefficients for the polynomial of x
    E = p["E"]  # bias, term at x=0
    return np.dot(np.vander(x, len(c) + 1)[:, :-1], c) + E


def make_prior(order, E):
    prior = gv.BufferDict()  # any dictionary works
    prior["a"] = [gv.gvar(0, 100) for i in range(order)]
    prior["E"] = gv.gvar(E[0], E[1])
    return prior


def make_fit_T(df, Ep, po, cut):
    prior = make_prior(po, Ep)
    datagv = make_data_eachT(df, cut)
    fit = ls.nonlinear_fit(data=datagv, fcn=fcn, prior=prior)
    print(fit)
    return fit


def parsing_args():
    parser = argparse.ArgumentParser(
        description="Fit Energy data (plot results and tabulate them)"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="../improv_runs/bmn2_su3_g20/e.csv",
        help="change default name of CSV file. (default: %(default)s)",
    )
    parser.add_argument(
        "--Lmin",
        type=float,
        default=16,
        help="Minimun lattice length. (default: %(default)s)",
    )
    parser.add_argument(
        "--prior",
        nargs="+",
        type=float,
        default=[10, 10],
        help="Energy prior. (default: %(default)s)",
    )
    args = parser.parse_args()
    print("Arguments passed")
    print(args)
    ########
    filename = args.file
    e_prior = args.prior
    L_min = args.Lmin
    if not os.path.isfile(filename):
        print("CSV file {} does not exist. Exiting.".format(filename))
        sys.exit()

    return filename, e_prior, L_min


def plot_results(results, L_min, figname):
    dx = pd.DataFrame(results, columns=["temp", "cut", "o", "E", "rchisq"])
    # start plotting
    fig, (ax1, ax2) = plt.subplots(
        2, sharex=True, figsize=(8, 6), gridspec_kw={"height_ratios": [4, 1]}
    )
    fig.subplots_adjust(hspace=0)
    ax2.set_xlim(0.0, 0.5)
    ax2.set_ylim(0, 5)

    en = dx.E.values
    avg_en = gv.mean(en)
    std_en = gv.sdev(en)
    ax1.set_ylim(np.amin(avg_en-5*std_en), np.amax(avg_en+5*std_en))
    te = dx.temp.values
    ch = dx.rchisq.values
    ax1.errorbar(te, avg_en, std_en, fmt="o", label=f"cut L: {int(L_min)}")
    ax2.plot(te, ch, linestyle="none", marker="s")
    ax2.axhline(1.0, color="black", linestyle="--")
    ax1.set_ylabel(r"$E_0$")
    ax2.set_ylabel(r"$\chi^{2}$/dof")
    ax2.set_xlabel(r"$T$")
    ax1.legend(loc="lower right")
    figname = figname.split("/")[-2]
    fig.savefig(f"plot_eachT_{figname}.jpg", dpi=150)
    print(f"Saving plot to plot_eachT_{figname}.jpg")
    plt.close(fig)


if __name__ == "__main__":
    filename, e_prior, Lcut = parsing_args()
    data = pd.read_csv(filename, sep=",", header=0, dtype=float)
    data["1/L"] = 1.0 / data["L"]
    temps = data.groupby("T")
    results = []
    po = 2  # order of polynomial fit in 1/L
    for g in temps.groups:
        df = temps.get_group(g)
        # fit
        print(f"************************************* temperature = {g}")
        fit = make_fit_T(df, e_prior, po, Lcut)
        results.append([g, Lcut, po, fit.p["E"], fit.chi2 / fit.dof])
    # print on screen
    print(
        tabulate(
            results,
            headers=["$T$", "$L_min$", "E", "$\chi^2$/dof"],
            floatfmt=".2f",
            tablefmt="latex_raw",
        )
    )
    # plotting limits are given automatically by 5\sigma
    plot_results(results, Lcut, filename)
