import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path
import fire
import matplotlib.pyplot as plt

sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
sns.set_context("poster")  # scale elements up or down in size


def make_kde_plot(
    Nt: str,
    Ts: list = ["04", "035", "03", "025", "02", "015", "01", "005", "0025"],
    run: str = "../lattice/improv_runs/bmn2_su3_g05",
    outputdir: str = "figures",
    outputfmt: str = "svg",
):
    # list where we save the energy of each temperature
    energies = []
    # list where we save the temperatures
    temperatures = []
    # loop over temperatures
    for T in Ts:
        try:
            filename = f"{run}/l{Nt}/t{T}/data.h5"
            data = pd.read_hdf(filename, "mcmc_obs")
            # append to lists
            energies.append(data.e.values)
            temperatures.append(data.temperature.values)
        except (ValueError, FileNotFoundError) as e:
            print(f"{e} . Skipping...")
    energies = np.concatenate(energies, axis=None)
    temperatures = np.concatenate(temperatures, axis=None)
    assert energies.shape == temperatures.shape
    df = pd.DataFrame(dict(t=temperatures, e=energies))
    t_order = list(df.t.unique())
    # Initialize the FacetGrid object
    pal = sns.cubehelix_palette(len(Ts), rot=-0.25, light=0.7)
    g = sns.FacetGrid(
        df, row="t", hue="t", hue_order=t_order, aspect=10, height=0.6, palette=pal
    )

    # Draw the densities in a few steps
    g.map(
        sns.kdeplot,
        "e",
        bw_adjust=0.5,
        clip_on=False,
        fill=True,
        alpha=1,
        linewidth=1.5,
    )
    g.map(sns.kdeplot, "e", clip_on=False, color="w", lw=2, bw_adjust=0.5)
    g.map(plt.axhline, y=0, lw=2, clip_on=False)

    # Define and use a simple function to label the plot in axes coordinates
    def label(x, color, label):
        ax = plt.gca()
        ax.text(
            0,
            0.2,
            label,
            fontweight="bold",
            color=color,
            ha="left",
            va="center",
            transform=ax.transAxes,
        )

    g.map(label, "e")
    g.set_xlabels(r"$E$")
    # Set the subplots to overlap
    g.fig.subplots_adjust(hspace=-0.25)

    # Remove axes details that don't play well with overlap
    g.set_titles("")
    g.set(yticks=[])
    g.despine(bottom=True, left=True)

    # save figure
    outputfile = f"{outputdir}/{run.split('/')[-1]}_l{Nt}_energy-kde_allT.{outputfmt}"
    g.savefig(outputfile)
    plt.close()


def main(
    datafolder: str = "../lattice/improv_runs/bmn2_su3_g05",
    outdir: str = "figures",
    outfmt: str = "svg",
):
    """Main function which will generate plots for all the parameters in the data folder.

    Args:
        datafolder (str, optional): The folder for a specific lattice coupling and gauge group. Defaults to "../lattice/improv_runs/bmn2_su3_g05".
        outdir (str, optional): The folder where we want to save the figures. Defaults to "figures".
        outfmt (str, optional): The format of the files (defines the filename extension). Defaults to "svg".
    """
    # possible n_t
    Ls = ["16", "24", "32", "48", "64", "96", "128", "192"]
    for Nt in Ls:
        print(f"L={float(Nt)}")
        make_kde_plot(Nt, run=datafolder, outputdir=outdir, outputfmt=outfmt)


if __name__ == "__main__":
    fire.Fire(main)
