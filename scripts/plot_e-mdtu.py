import pandas as pd
import seaborn as sns
from pathlib import Path
import fire
import matplotlib.pyplot as plt

sns.set_theme(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})
sns.set_context("poster")  # scale elements up or down in size


def make_joint_plot_e_mdtu(
    run: str = "../lattice/improv_runs/bmn2_su3_g05/l16/t04",
    outputdir: str = "figures",
    outputfmt: str = "svg",
):
    """Use seaborn JointGrid to create a plot showing the MCMC trajectory of the energy as a function of MDTU
    for a single run.
    The plot is augmented by marginal distributions of energy and mdtu on the two axis.
    We save the plot in SVF format for WEB publising, or PDF format for paper visualization.

    Args:
        run (str, optional): The folder where the raw run data is expected to be (it will look here for a file called data.h5). Defaults to "../../lattice/improv_runs/bmn2_su3_g05/l16/t04".
        outputdir (str, optional): The folder where we want to save the plot. Defaults to "../figures".
        outputfmt (str, optional): The extension of the plot file which will decide the format used for saving on disk. Defaults to "svg".
    """
    # read data from disk
    try:
        filename = f"{run}/data.h5"
        data = pd.read_hdf(filename, "mcmc_obs")
    except (ValueError, FileNotFoundError) as e:
        print(f"{e} . Skipping...")
        return
    # color palette
    pal = sns.cubehelix_palette(data.ntau.nunique(), rot=-0.5, light=0.7)
    g = sns.JointGrid(
        data=data,
        x="mdtu",
        y="e",
        hue="ntau",
        height=10,
        palette=pal,
        marginal_ticks=True,
    )
    # Add the joint and marginal histogram plots
    g.plot_joint(sns.lineplot)
    g.plot_marginals(sns.histplot)
    # labels
    legend_properties = {"weight": "bold", "size": 10}
    g.ax_joint.legend(
        prop=legend_properties, facecolor="white", loc="lower right", title=r"$n_\tau$"
    )
    g.set_axis_labels(xlabel="MDTU", ylabel=r"$E$")
    # save
    names = run.split("/")
    outputfile = (
        f"{outputdir}/{names[-3]}_{names[-2]}_{names[-1]}_energy-mdtu.{outputfmt}"
    )
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
    runs = Path(datafolder)
    for run in runs.rglob("l*/t*"):
        print(f"{run}")
        make_joint_plot_e_mdtu(run=str(run), outputdir=outdir, outputfmt=outfmt)


if __name__ == "__main__":
    fire.Fire(main)
