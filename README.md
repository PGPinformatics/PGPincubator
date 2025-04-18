# Personal Genome Project incubator

## Vision

The PGPincubator is an effort to create a distribution of open data,
tools, workflows, AI models and learning materials that support
validation, benchmarking, and education in bioinformatics and
biomedicine for precision health and (pre-clinical) biomedical AI.  In
addition, the incubator is a distributed network of physical computing
infrastructure used to test components included in the distribution,
such as validating genomics workflows or benchmarking AI models.

To help hatch this network, PGPincubator is creating a network (using
Tailscale) of “h-grams.”  A h-gram is 1-4 microSD cards (3-4 weigh
about a gram!) each flashed with a bootable operating system image and
pre-loaded with data and tools.  The PGPincubator open source project
develops and maintains the scripts, process documentation and data
resources required to build / test the h-gram image.  These h-grams
can then be booted on compatible commodity PC hardware.  The operating
system (Ubuntu) is pre-configured to act as a server suitable for
home, office or lab and is accessed by other devices through a
browser.  Each h-gram will be pre-loaded with hundreds of gigabytes of
openly licensed infrastructure software, bioinformatics tools, genomic
datasets, AI models, and learning resources — making them ideal for
education, validation, and benchmarking in biomedical research.

Instances of the PGPi h-gram can connect to form a private network
using a VPN, forming a distributed cluster via federation.  For
students and researchers who do not have access to a HPC system or
cloud budget, and are working on PGPi open data, the PGPi network may
eventually make it possible to run significant data analysis on
contributed, cooperating compute resources.  The h-gram operating
system is also pre-configured with drivers for consumer GPUs to make
it easy to run GPU-accelerated scientific analysis, machine learning
and large language models.  The PGPi h-gram can be thought of as a
fully loaded lab bench — already assembled, stocked, and ready to use.

The PGPincubator data and software distribution pre-loaded on the
h-gram will be updated on a 6 month release schedule, inspired by
Linux distribution releases.  With both software and data sets
distributed in versioned releases, it becomes far easier for
researchers to precisely identify both software and data used in their
work, for others to reproduce that work, and for students to study
that work, while ensuring that validation and benchmarking methods are
done fairly against a common baseline.

# Recipes

Currently conducting research and development around supporting software and tooling.

* [Host setup and base image](recipes/Create-base-image-for-Arvados/Create-base-image-for-Arvados.md) (based on R7, supposed to be generic)
* [Single-host single-hostname installation](recipes/Install-Arvados-instance-over-base-image.md) on base
* [Minimal host setup](recipes/Minimal-install-of-AMD-ROCm-for-Docker-images.md) that supports running ROCm-based apps on GPU in a container (based on UM790XTX OR W7900Pro)
* [Running ROCm-powered llamafile with GPU in a container](recipes/llamafile-with-ROCm-in-container.md)
* [Passing through SATA controller for use by the guest, with disk encryption setup](recipes/SATA-controller-passthrough-for-guest.md)

## Running demos

* Very much TBD, do not use yet: [\[TBD\] Guide for running the guest-to-host GPU-enabled pipeline with llamafile](recipes/Guide-for-running-the-guest-to-host-GPU-enabled-pipeline-with-llamafile.md)
* [Running complete human WGS processing workflow locally](recipes/Running-complete-human-WGS-processing-workflow-locally.md)

## Related recipes

* (Generic guide) [Invoking docker to run containers with GPU support](recipes/Invoking-docker-to-run-containers-with-GPU-support.md)

## System admin fragments

* [Creating a Memtest86+ bootable USB drive that works with UEFI](recipes/UEFI-compatible-Memtest86+-on-bootable-USB.md)
* [Pre-initializating EXT4 filesystem on hard drive](recipes/Pre-initializating-EXT4-filesystem-on-hard-drive.md)
* [Testing network bandwidth with `iperf3`](recipes/Testing-network-bandwidth-with-iperf3.md)
* [Remove a user from GDM login selection screen](recipes/Prevent-GNOME-display-manager-GDM3-from-showing-a-certain-user.md)
* [Change the GDM login screen logo](recipes/Login-screen-logo.md)
* [Creating a GNOME desktop shortcut](recipes/Creating-desktop-shortcut.md)
