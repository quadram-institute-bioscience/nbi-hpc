---
title: Quick tips
---

## bashrc

All these snippets can be added to your `~/.bashrc`.

1) Enable core bioinformatics packages in the search from `module avail`:

```bash
# Enable Core Bioinformatics modules
module use /qib/research-projects/bioboxes/lua
```

2) Configure some useful variables for Nextflow:

```bash
# Nextflow settings
export NXF_ANSI_LOG=false
export NXF_OFFLINE='true'
export NXF_SINGULARITY_CACHEDIR="/qib/platforms/Informatics/transfer/outgoing/singularity/nxf"
```


3) Configure some handy locations:
 
```bash
# Configure shortcuts for some QIB locations
export SCRATCH=/qib/scratch/users/$USER/
export PACKAGES=/nbi/software/testing/bin/
export OUTGOING=/qib/platforms/Informatics/transfer/outgoing
export INCOMING=/qib/platforms/Informatics/transfer/incoming
export DATABASES=/qib/platforms/Informatics/transfer/outgoing/databases/
```