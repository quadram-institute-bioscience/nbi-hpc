---
title: Installing
---

## Installing Micromamba

> See a full [micromamba tutorial](https://telatin.github.io/microbiome-bioinformatics/Install-Micromamba/) for a general background

You will need to be in the "Software node" to be able to download:

```bash
# Connect to the HPC first if you are not already in the login node
ssh ${USER}@nbi.ac.uk

# Then connect to the "software node"
ssh software
```

Then you can download the Micromamba installer, and execute it

```bash
# This will download and run the micromamba installer
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
```

## ⚠️ Using the channels from NBI

Using `nano` or your favourite editor, change `~/.condarc` to look like:

```yaml
channel_alias: https://repo.prefix.dev/
channels:
  - conda-forge
  - bioconda
channel_priority: strict
```

You will probably just need to add the first line (`channel_alias...`). This is important,
as our network block connection to the default channels.

If the "channels" list contains *defaults*, or *r*, please remove them as they are not needed and
not available from our network.