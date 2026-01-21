---
title: Configure your account
---

## Some tips

```bash
# Enable Core Bioinformatics modules
module use /qib/research-projects/bioboxes/lua
```

```bash
# Nextflow settings
export NXF_ANSI_LOG=false
export NXF_OFFLINE='true'
export NXF_SINGULARITY_CACHEDIR="/qib/platforms/Informatics/transfer/outgoing/singularity/nxf"
```

```bash
# Configure shortcuts for some QIB locations
export SCRATCH=/qib/scratch/users/$USER/
export PACKAGES=/nbi/software/testing/bin/
export OUTGOING=/qib/platforms/Informatics/transfer/outgoing
export INCOMING=/qib/platforms/Informatics/transfer/incoming
export DATABASES=/qib/platforms/Informatics/transfer/outgoing/databases/
```