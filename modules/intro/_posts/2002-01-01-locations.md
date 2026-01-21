---
title: "Locations"
---

## Home directory

When you log in the NBI HPC you will be in your home directory. This is a location only accessible to you
where you can store scripts and your own "Micromamba" environments.

You shouldn't store any important file in your home directory, and especially avoid performing analyses here:
there is a dedicated location for that!

## Primary ISILON

Each research group has a special directory where each member of the group has read and write access to.
By default every member of staff with the same line manager (Group Leader) will have access to this directory,
but you can ask to grant permissions to collaborators.

For QIB users these will be `/qib/research-groups/Name-Surname/`:

You can see existing directories with:
```
ls /qib/research-groups/
```

💡 This is the location you should use for your analyses: it's shared with your team, is regularly backed up and
you can easily restore from backups if needed.

Similarily to *research-groups*, which is dedicated to teams, there is a parallel *research-projects* directory.
The second could be the right place for collaborations across groups: you can ask your support teams to create a 
dedicated project directory specifying who should have access to it.

### Accessing your HPC locations from Windows

From any Windows machine operated by NBI and connected to the NBI network (phisically or via VPN),
you can type `\\qib-hpc-data` to see your HPC folders, including your Home Directory, the Research-Groups and the Research-Projects locations:

![Windows Explorer]({{ site.baseurl }}/{% link img/win.png %})

### Accessing your HPC locations from Mac

Similarily, from MacOS open the Finder, and then press Cmd+K (or "Go -> Connect to server..." from the menu bar),
and type `smb://qib-hpc-data.nbi.ac.uk` as shown in the figure:

![Windows Explorer]({{ site.baseurl }}/{% link img/finder.png %})


## Scratch space

When doing analyses you might want a "scratch space": a directory that is not backed up but it's accessible from all the cluster nodes.
You fill find yours in `/qib/scratch/users/$USER`.

## Galaxy locations

🌌...