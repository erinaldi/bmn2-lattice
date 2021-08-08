# Analysis of Lattice Monte Carlo data for matrix quantum mechanics

We collect data for the bosonic matrix model with 2 matrices and gauge group SU(2).
The results are reported in the publication [Rinaldi et al. (2021)](www.arxiv.org/abs/2108.00000).
Consider the citation in [Cite](#cite).


# Code
## Installation

You can install the dependencies for the scripts and the notebooks using [conda](https://docs.conda.io/projects/conda/en/latest/)
```bash
conda env create -f environment.yml
```

Check that the `lattice-fits` environment has been created and then activate it
```bash
conda env list
conda activate lattice-fits
```

## Scripts

The scripts rely on the presence of lattice data in an external folder.
The data is collected by [scripts/gather_data.py](./scripts/gather_data.py) in various `HDF5` files and they will be provided as an archive upon publication of the paper.

Figures and tables of the processed lattice data can be found online on the paper's supplementary material [website](https://erinaldi.github.io/mm-qc-dl-supplemental/).
Check out the [Lattice Monte Carlo](https://erinaldi.github.io/mm-qc-dl-supplemental/mc/mc/) section.

# Cite

If you use this code (or parts of it), please consider citing our paper:
```bibtex
@misc{rinaldi2021matrixmodels,
    title   = {Matrix Model simulations using Quantum Computing, Deep Learning, and Lattice Monte Carlo}, 
    author  = {Rinaldi, Enrico and Han, Xizhi and Hassan, Mohammad and Feng, Yuan and Nori, Franco and McGuigan, Michael and Hanada, Masanori},
    year    = {2021},
    eprint  = {2108.00000},
    archivePrefix = {arXiv},
    primaryClass = {quant-ph}
}
```