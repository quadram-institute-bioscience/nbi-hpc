---
title: Using SLURM
---

## Checking existing jobs

Once you start submitting jobs, you'll want to know what's happening: is your job running? Waiting in queue? Already finished?

The **`squeue`** command shows the job queue:

```bash
squeue
```

This displays all jobs on the cluster — which can be overwhelming. To see only your own jobs:

```bash
squeue -u $USER
```

The output shows key information for each job:

| Column | Meaning |
|--------|---------|
| JOBID | Unique identifier for the job |
| PARTITION | Which partition the job runs on |
| NAME | Job name (from your script or `--job-name`) |
| USER | Who submitted it |
| ST | State: `R` (running), `PD` (pending), `CG` (completing) |
| TIME | How long it's been running |
| NODES | Number of nodes allocated |
| NODELIST | Which node(s) it's running on |

The default output can be cramped. For a cleaner view, try:

```bash
squeue -u $USER -o "%.10i %.12j %.8T %.10M %.4C %.8m %R"
```

This shows: job ID, name, state, time, cores, memory, and the reason if pending.

**Pro tip**: add an alias to your `~/.bashrc` for quick access:

```bash
alias myq='squeue -u $USER -o "%.10i %.12j %.8T %.10M %.4C %.8m %R"'
```

To check details of a specific job (including finished ones), use **`sacct`**:

```bash
sacct -j 123456 --format=JobID,JobName,State,Elapsed,MaxRSS,ExitCode
```

This is especially useful to see how much memory your job *actually* used (`MaxRSS`) — handy for optimising future requests.

## Creating a Slurm script

> There is a convenient [Slurm script configurator](https://quadram-institute-bioscience.github.io/nbi-hpc/maker/) in this website


A Slurm script is simply a bash script with special `#SBATCH` directives that tell the scheduler what resources you need. These directives look like comments to bash, but Slurm reads them when you submit the job.

Here's a minimal example — save it as `test_job.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=test_job
#SBATCH --output=test_%j.out
#SBATCH --error=test_%j.err
#SBATCH --mem=1g
#SBATCH --cpus-per-task=1
#SBATCH --time=0:10:0
#SBATCH --partition=qib-short

echo "Job started at $(date)"
echo "Running on node: $(hostname)"
echo "Working directory: $(pwd)"

sleep 60

echo "Job finished at $(date)"
```

Let's break down the directives:

| Directive | Purpose |
|-----------|---------|
| `--job-name` | A human-readable name (shows in `squeue`) |
| `--output` | File for standard output (`%j` expands to job ID) |
| `--error` | File for standard error |
| `--mem` | Memory request (e.g., `1g`, `500m`, `16g`) |
| `--cpus-per-task` | Number of CPU cores |
| `--time` | Maximum runtime (`HH:MM:SS` or `D-HH:MM`) |
| `--partition` | Which partition to submit to |

Submit the job with:

```bash
sbatch test_job.sh
```

Slurm will return a job ID:

```
Submitted batch job 123456
```

Monitor it with `squeue -u $USER`, and once complete, check the output:

```bash
cat test_123456.out
```

A few practical tips:

- **Always request realistic resources** — asking for 100 GB when you need 4 GB wastes cluster capacity and may delay your job
- **Use `%j` in output filenames** — this prevents jobs from overwriting each other's logs
- **Start with short test runs** — debug with 10 minutes and small data before launching a 3-day job

 