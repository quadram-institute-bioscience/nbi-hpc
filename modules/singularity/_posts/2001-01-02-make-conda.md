---
title: Creating a container from conda
---

Sometimes you need a container with multiple related tools — for example, a complete environment for long-read genome assembly. 
Installing each tool manually would be tedious and error-prone. 

Instead, we can use **Pixi**, a fast package manager that works with Conda/Bioconda packages, to handle all the dependencies for us.

This tutorial shows how to create a Singularity container with **Unicycler** and several 
supporting assemblers and utilities for hybrid and long-read assembly workflows.

## The definition file

Create a file called `assembly-tools.def`:

```yaml
Bootstrap: docker
From: ubuntu:24.04

%labels
    Author Core Bioinformatics
    Description Long-read and hybrid assembly tools (Unicycler, Flye, Canu, Raven, etc.)

%environment
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
    export PATH="/opt/software/.pixi/envs/default/bin:$PATH"

%post
    # Update package lists and install essential packages
    apt-get update && apt-get install -y \
        build-essential \
        git \
        wget \
        curl \
        nano \
        zlib1g-dev \
        ca-certificates \
        locales \
        && rm -rf /var/lib/apt/lists/*

    # Generate locale for proper Unicode support
    locale-gen en_US.UTF-8

    # Create software directory
    mkdir -p /opt/software
    cd /opt/software

    # Install pixi package manager
    curl -fsSL https://pixi.sh/install.sh | bash
    export PATH="$HOME/.pixi/bin:$PATH"

    # Create pixi.toml configuration with all required packages
    cat > pixi.toml << 'EOF'
[project]
name = "assembly-env"
version = "1.0.0"
description = "Long-read and hybrid assembly environment"
channels = ["https://repo.prefix.dev/conda-forge", "https://repo.prefix.dev/bioconda"]
platforms = ["linux-64"]

[dependencies]
# Hybrid assembler
unicycler = "0.5.*"

# Long-read assemblers
canu = "2.3.*"
flye = "2.9.*"
miniasm = ">=0.3"
raven-assembler = ">=1.8.3"
wtdbg = ">=2.5"

# Polishing and support tools
minipolish = ">=0.2.0"
racon = ">=1.5.0"
minimap2 = ">=2.28"

# Utilities
any2fasta = "0.4.*"
seqtk = ">=1.4"
EOF

    # Install all packages
    /root/.pixi/bin/pixi install

    # Clean up apt cache
    apt-get clean

%runscript
    exec "$@"

%test
    # Verify key tools are accessible
    unicycler --version
    flye --version
    minimap2 --version
```

### Understanding the definition file

#### Base image and metadata

```singularity
Bootstrap: docker
From: ubuntu:24.04

%labels
    Author Core Bioinformatics
    Description Long-read and hybrid assembly tools (Unicycler, Flye, Canu, Raven, etc.)
```

We start from Ubuntu 24.04 and add labels for documentation.

#### Environment variables

```singularity
%environment
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
    export PATH="/opt/software/.pixi/envs/default/bin:$PATH"
```

These are set at **runtime** (when you use the container):

| Variable | Purpose |
|----------|---------|
| `LC_ALL`, `LANG` | Proper UTF-8 locale support — prevents encoding errors |
| `PATH` | Adds the Pixi environment's bin directory so all installed tools are available |

#### The %post section

This runs during the build, as root.

**System dependencies**

```bash
apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    curl \
    nano \
    zlib1g-dev \
    ca-certificates \
    locales \
    && rm -rf /var/lib/apt/lists/*
```

| Package | Purpose |
|---------|---------|
| `build-essential` | Compilers, in case any package needs compilation |
| `git`, `wget`, `curl` | Download tools |
| `nano` | A simple editor for debugging inside the container |
| `zlib1g-dev` | Compression library (common dependency) |
| `ca-certificates` | SSL certificates for HTTPS downloads |
| `locales` | Required for locale generation |

**Installing Pixi**

```singularity
mkdir -p /opt/software
cd /opt/software
curl -fsSL https://pixi.sh/install.sh | bash
export PATH="$HOME/.pixi/bin:$PATH"
```

Pixi is a modern, fast package manager compatible with Conda packages. 
It installs to `~/.pixi/bin` by default.

#### The pixi.toml configuration

> This is the section that you are likely to change with a list
> of packages required in your environment (container)

```toml
[project]
name = "assembly-env"
version = "1.0.0"
description = "Long-read and hybrid assembly environment"
channels = ["https://repo.prefix.dev/conda-forge", "https://repo.prefix.dev/bioconda"]
platforms = ["linux-64"]

[dependencies]
unicycler = "0.5.*"
canu = "2.3.*"
flye = "2.9.*"
# ... etc
```

This is Pixi's configuration format, similar to a Conda environment file but in TOML. Key points:

- **channels**: We use `conda-forge` (general packages) and `bioconda` (bioinformatics tools)
- **platforms**: We only need `linux-64` for HPC use
- **dependencies**: Version constraints use standard syntax — `0.5.*` means any 0.5.x version, `>=2.28` means 2.28 or newer

### Included tools

| Tool | Purpose |
|------|---------|
| **unicycler** | Hybrid assembler for bacterial genomes (Illumina + long reads) |
| **flye** | Long-read assembler, good for high-error reads |
| **canu** | Long-read assembler with built-in correction |
| **miniasm** | Ultra-fast long-read assembler (no correction) |
| **raven-assembler** | Fast and accurate long-read assembler |
| **wtdbg** | Very fast assembler for long reads |
| **minipolish** | Polishes miniasm assemblies using Racon |
| **racon** | Consensus module for polishing assemblies |
| **minimap2** | Fast aligner for long reads |
| **any2fasta** | Convert various formats to FASTA |
| **seqtk** | Swiss-army knife for sequence manipulation |

### The runscript

```singularity
%runscript
    exec "$@"
```

This passes any command directly to the container. Unlike the vsearch example (which defaulted to running vsearch), this container lets you run any of the installed tools:

```bash
./assembly-tools.sif unicycler --help
./assembly-tools.sif flye --help
```

### Testing

```singularity
%test
    unicycler --version
    flye --version
    minimap2 --version
```

Verifies that key tools are correctly installed and accessible.

## Building the container

```bash
sudo singularity build assembly-tools.sif assembly-tools.def
```

This will take several minutes as Pixi downloads and installs all the packages.

## Using the container

### Running individual tools

```bash
# Run unicycler
singularity exec assembly-tools.sif unicycler -1 reads_R1.fq.gz -2 reads_R2.fq.gz -l long_reads.fq.gz -o output

# Run flye
singularity exec assembly-tools.sif flye --nano-raw long_reads.fq.gz --out-dir flye_out --threads 16

# Run minimap2
singularity exec assembly-tools.sif minimap2 -ax map-ont ref.fa reads.fq > aligned.sam
```

### In a Slurm script

A simple example: 

```bash
#!/bin/bash
#SBATCH --job-name=assembly
#SBATCH --cpus-per-task=16
#SBATCH --mem=64g
#SBATCH --time=1-0

CONTAINER=/path/to/assembly-tools.sif

singularity exec $CONTAINER flye \
    --nano-hq long_reads.fq.gz \
    --out-dir flye_assembly \
    --threads $SLURM_CPUS_PER_TASK
``` 

 