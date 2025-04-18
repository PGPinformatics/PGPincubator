= Personal Genome Project incubator

== Vision

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

= Current status

Currently conducting research and development around tooling.

See [Arvados recipes index](recipes/Arvadosrecipesindex.html)
