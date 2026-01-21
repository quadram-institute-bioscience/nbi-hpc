---
title: Using Micromamba
---

Micromamba is a lightweight Conda-compatible package manager
that lets you create **reproducible software environments** 
without needing admin rights.

On the NBI HPC, you should 
**create and modify environments only on the _software node_** 
(compilation and downloads are allowed there).  
Compute jobs should use environments that are already created.



## Create an environment

```bash
# Create a test environment (you MUST be in the software node!)
micromamba create -n env1 samtools=1.18 minimap2 seqfu
```

💡 We enabled the `conda-forge` and `bioconda` channels via configuration

---

## Some basic commands

To list all  the environments available in our installation:

```bash
micromamba env list
```

To activate one environment (by name):

```bash
# Activate the base environment
micromamba activate base
```

Running a command from an environment:

```bash
# Simply run a command without activating
micromamba run -n env1 seqfu version

# or activate first 
micromamba activate env1
seqfu version
```

---

## Create an environment from a YAML file 

If you want an environment that is easy to share and reproduce, use a YAML file.

Example `environment.yml`:

```yaml
name: env1
channels:
  - conda-forge
  - bioconda
dependencies:
  - samtools=1.18
  - minimap2
  - seqfu
```

Create it:

```bash
micromamba env create -f environment.yml
```

💡 You can export an environment with `micromamba env export` and save it as YAML file.

---

## Install, update, and remove packages

Install a new package into an existing environment:

```bash
micromamba install -n env1 fastp
```

Update a package:

```bash
micromamba update -n env1 samtools
```

Remove a package:

```bash
micromamba remove -n env1 fastp
```

---

## Remove an environment

```bash
micromamba env remove -n env1
```

---

## Where are environments stored?

You can check where micromamba stores environments with:

```bash
micromamba info
```

On HPC systems, environments are usually stored under your home directory (or another user-writable location).
If you want to keep environments in a dedicated folder (recommended), you can set:

```bash
export MAMBA_ROOT_PREFIX=$HOME/micromamba
```

(You can add this to your `~/.bashrc` if your site policy allows it.)

---

## Using micromamba inside an `sbatch` job

You typically **do not want to run `micromamba create` inside a job**.
Instead, create the environment once on the software node, then use it in jobs.

Example `sbatch` script:

```bash
#!/usr/bin/env bash
#SBATCH --job-name=mm_env_test
#SBATCH --partition=qib-short
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=slurm-%j.out

set -euo pipefail

# Option A: run without activating (clean and safe)
micromamba run -n env1 seqfu version
micromamba run -n env1 samtools --version
micromamba run -n env1 minimap2 --version
```

---

## Common troubleshooting

### `micromamba: command not found`

You may need to load it via modules (if available) or ensure it is in your `PATH`.

Try:

```bash
which micromamba
```

 
### Environment activates but tools are missing

Check you are using the correct environment:

```bash
micromamba env list
micromamba list -n env1
```

 