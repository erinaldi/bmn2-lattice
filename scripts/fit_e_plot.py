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

plt.rc("text", usetex=True)
plt.style.use("figures/paper.mplstyle")


def make_data(data, cut=0.45):
    df = data.query("`1/LT` < @cut")  # .drop_duplicates(subset="1/LT")
    x = df["1/LT"].values
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


def make_fit(data, Ep, po, cut):
    prior = make_prior(po, Ep)
    datagv = make_data(data, cut)
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
        default="../lattice/improv_runs/bmn2_su3_g20/e.csv",
        help="change default name of CSV file. (default: %(default)s)",
    )
    parser.add_argument(
        "--prior",
        nargs="+",
        type=float,
        default=[9, 9],
        help="Energy prior. (default: %(default)s)",
    )
    args = parser.parse_args()
    print("Arguments passed")
    print(args)
    ########
    filename = args.file
    e_prior = args.prior
    # a_max = args.amax
    if not os.path.isfile(filename):
        print("CSV file {} does not exist. Exiting.".format(filename))
        sys.exit()

    return filename, e_prior  # , a_max


def plot_results(results, e_lim, figname):
    df = pd.DataFrame(results, columns=["cut", "N", "E", "rchisq"])
    # start plotting
    fig, (ax1, ax2) = plt.subplots(
        2, sharex=True, figsize=(8, 6), gridspec_kw={"height_ratios": [4, 1]}
    )
    fig.subplots_adjust(hspace=0)
    ax2.set_xlim(0.0, 0.6)
    ax1.set_ylim(e_lim[0], e_lim[1])
    #    ax1.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=8))
    ax2.set_ylim(0, 5)

    for i, o in enumerate(df.N.unique()):
        # filter data
        dff = df.query("N==@o")
        # plot
        ax1.errorbar(
            dff.cut + i / 200,
            gv.mean(dff.E.values),
            gv.sdev(dff.E.values),
            fmt="o",
            label=r"$n_p$" + f"={o}",
        )
        ax2.plot(dff.cut + i / 200, dff.rchisq, linestyle="none", marker="s")

    ax2.axhline(1.0, color="black", linestyle="--")
    ax1.set_ylabel(r"$E_0$")
    ax2.set_ylabel(r"$\chi^{2}$/dof")
    ax2.set_xlabel(r"$a_\textrm{max}$")
    #    ax1.set_title(r"SU(3) $\lambda=2.0$")
    ax1.legend(loc="upper right")
    figname = figname.split("/")[-2]
    fig.savefig(f"figures/{figname}_energy-fit_allT.pdf")
    fig.savefig(f"figures/{figname}_energy-fit_allT.png")
    print(f"Saving plot to plot_{figname}.pdf")
    plt.close(fig)


if __name__ == "__main__":
    """Make fits of 1/LT function for each cut in 1/LT and for different polynomial orders.
    Plot the results in a PDF.
    """
    filename, e_prior = parsing_args()
    data = pd.read_csv(filename, sep=",", header=0, dtype=float)
    data["1/LT"] = 1.0 / (data["L"] * data["T"])
    results = []
    for cut in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]:
        for po in [1, 2, 3]:
            print(f"************************************* cut= {cut} order = {po}")
            fit = make_fit(data, e_prior, po, cut)
            results.append([cut, po, fit.p["E"], fit.chi2 / fit.dof])

    # saving table
    outfilename = filename.split("/")[-2]
    outfile = f"tables/{outfilename}_fit_e_allT.tex"
    print(f"Saving to {outfile}")
    with open(outfile, "w") as f:
        print(
            tabulate(
                results,
                headers=["$a_\\textrm{max}$", "$n_p$", "E", "$\chi^2$/dof"],
                floatfmt=".2f",
                tablefmt="latex_raw",
            ),
            file=f,
        )
    # plotting limits are given automatically by 10\sigma
    e_lims = [
        fit.p["E"].mean - 10 * fit.p["E"].sdev,
        fit.p["E"].mean + 10 * fit.p["E"].sdev,
    ]
    plot_results(results, e_lims, filename)
