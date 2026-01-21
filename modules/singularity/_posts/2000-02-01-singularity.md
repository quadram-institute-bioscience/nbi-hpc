---
title: Using Singularity containers
---


> See a complete [tutorial on Singularity/Apptainer](https://mambelli.github.io/hsf-training-apptainer/instructor/index.html)

Singularity is now called Apptainer, but in our cluster is still going by the `singularity` command.

From your terminal you can get the date with `date`, but it's going to be a boring date:

```bash
date
# will print something like 'Wed 21 Jan 11:43:30 GMT 2026'
```

We need a better tool, that prints something like:
```
 ______________________________
< Wed Jan 21 11:42:59 UTC 2026 >
 ------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

Instead of installing the program, we will run a container that contains it to have a first hands-on experience of a container


## Downloading the container

Singularity containers are stored in images (files) that can be easily shared and copied. In general, you might simply download or copy a file to get a new Singularity container. Alternatively, we can get containers from online repositories - similar to Docker Hub.

```
# Since we need internet, let's go to the software node
ssh software

# Let's download an image for `lolcow`
singularity pull library://lolcow

# check what you just downloaded (should include lolcow_latest.sif)
ls -ltr | tail
```

## Running a tool from the container

Each container has an entire system in it (potentially with a lot of tools).  To execute a single tool (program) from a container we use this syntax:

```bash
singularity exec $IMAGE $COMMAND

# for example:
singularity exec lolcow_latest.sif  cowsay "NBI HPC!"
```

The command means run the `cowsay "NBI HPC!"` command, but using the tool from *lolcow_latest.sif*.

## Executing the container

While *exec* allows to run any tool that is available inside the container, there is a special *run* command to
execute a special script (if available) that is the entry point of the image.

We can confirm that lolcow has an entry point:
```bash
# Check what would be executed by the image itself
singularity inspect --runscript lolcow_latest.sif

# Run the script! Simply:
singularity run lolcow_latest.sif
```