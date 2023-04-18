# Contributing to planbelt
Welcome! Planbelt is a collection of tools for planners and anyone else who might be interested. 

## Setup

All the requirements are in the environment.yml file. For now, Conda/Mamba are used, but a requirements.txt will be added in the future for those who prefer not to use those tools.
In a terminal, run:
```conda env create -f environment.yml```
to get started. If you have Mamba installed, you can swap it in for Conda above if desired (will solve the environment a bit faster)

Then run:
```conda activate planbelt```


Planbelt uses conventional commits to automate version updates using semantic versioning. On my own machine, I use commitizen to help stick to conventional commit formats.
If you prefer not to use commitizen, that's totally fine, but there are still some hooks you'll need to install. With your conda environment activated, run:

```pre-commit install --hook-type commit-msg --hook-type pre-push```

