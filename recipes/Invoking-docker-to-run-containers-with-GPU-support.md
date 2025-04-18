# Invoking `docker` to run containers with GPU support

# Problem statement

To run a Docker container that must access discrete GPU (dGPU) cards (for example, to run LLM inference), we should explicitly put the correct device files corresponding to those cards on the command line of "`docker run`", while avoiding the computer's integrated GPU (iGPU).

To do this, we have to find out these device files' paths, which vary from one system to another. As a prerequisite, we should have some idea about the model of our card(s).

# TODO

- How do we make sure the drivers are already installed? If not, how to fix them (already written elsewhere; need cleanup)  
- Write about adding the 'render' group to the container, which is needed for read-write access to the card device file by an unprivileged user. With Docker, this simple step could be plagued by this issue: [https://github.com/docker/compose/issues/7277](https://github.com/docker/compose/issues/7277) (unable to add group by group name) which resurfaces now and then. This is not necessary if the container runs as root.

# Assumptions

This guide assumes that we are using AMD graphic cards, and that the correct AMDGPU kernel driver is installed and in use.

# Identify AMD graphic card(s)

First, update the PCI device IDs to help finding the device easier:

`sudo update-pciids`

Then, do this to list all PCI devices:

`sudo lspci | less`

Search for the GPU – For AMD cards, use the search string "`ATI`" in the paged output (press `/` \[slash\], then type `ATI` \[in uppercase\], and Enter)

We should see something like this:

`[...]`  
`05:00.0 PCI bridge: Advanced Micro Devices, Inc. [AMD/ATI] Navi 10 XL Upstream Port of PCI Express Switch (rev 12)`  
`06:00.0 PCI bridge: Advanced Micro Devices, Inc. [AMD/ATI] Navi 10 XL Downstream Port of PCI Express Switch (rev 12)`  
`07:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Navi 33 [Radeon RX 7600/7600 XT/7600M XT/7600S/7700S / PRO W7600] (rev c0)`  
`07:00.1 Audio device: Advanced Micro Devices, Inc. [AMD/ATI] Navi 31 HDMI/DP Audio`  
`c8:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Phoenix1 (rev c1)`  
`c8:00.1 Audio device: Advanced Micro Devices, Inc. [AMD/ATI] Rembrandt Radeon High Definition Audio Controller`  
`[...]`

Here, we can see (highlighted) that the dGPU device is listed (we know this is the one, by the product model). Note the corresponding ID, in this case `07:00.0`. This number will help us identify the device file.

The actual device is likely different from the one shown here. But in general it should be identifiable by its type ("VGA compatible controller" or similar) and the make and model name.

# Identify device files

Now look at the output of

`ls -l /dev/dri/by-path`

The output will look like the following,

`lrwxrwxrwx 1 root root  8 Feb 12 18:11 pci-0000:07:00.0-card -> ../card1`  
`lrwxrwxrwx 1 root root 13 Feb 12 16:21 pci-0000:07:00.0-render -> ../renderD128`  
`lrwxrwxrwx 1 root root  8 Feb 13 09:33 pci-0000:c8:00.0-card -> ../card2`  
`lrwxrwxrwx 1 root root 13 Feb 12 16:21 pci-0000:c8:00.0-render -> ../renderD129`

What this means is that the device we just identified by the PCI id `07:00.0` is mapped to the path `/dev/dri/renderD128`

And we have now found the device to be passed to Docker containers.

# Invoke "`docker run`"

To run any docker container that needs GPU access, we should pass the device path to the container when invoking the '`docker run`' command, in the following fashion:

`docker run --device=/dev/kfd --device=/dev/dri/renderD128 [...other arguments...]`

The `--device=...` arguments should appear in addition to any other arguments to "`docker run`" that are necessary for the container to work. The `--device=/dev/kfd` argument is also necessary. 

# Multiple GPUs

If multiple GPUs should be passed to the container, in the first step we should find all of them, and repeat the `--device=...` arguments for each GPU device on the commandline. For example

`docker run --device=/dev/kfd --device=/dev/dri/renderD128 --device=/dev/dri/renderD129 [...]`

Notice that when we use a ROCm-based image, in general we should *NOT* pass the computer's integrated GPU to the container. In the above example, the iGPU corresponds to the following line in the `lspci` output:

`c8:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Phoenix1 (rev c1)`

# When reusing stopped container

If we want to reuse a stopped container that has been created by the correct incantation, we don't need to repeat any of the steps. We can simply use the "`docker start [container_name]`" command to bring the container to life, and as long as the device files are still there, we will be fine.