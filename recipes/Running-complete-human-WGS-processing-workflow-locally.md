# Running complete human WGS processing workflow locally

The purpose of these step-by-step guides is to show the procedures and parameter modifications that lead to a complete WGS processing pipeline that will likely finish without issues.

This document references data hashes to input data collection on pirca, currently without guess access.

This guide has been tested on the WTR PRO (storage unit). The machine has 8 CPU cores that show up as 16 logical cores with HT. The Arvados guest on the WTR PRO is assigned all 16 cores, and 40 GB of RAM (generous so that the pipelines run without failing; looking forward to lowering it based on resource usage auditing data).

To begin, we assume that the Arvados Python and CWL SDK commandline tools have been [installed](https://doc.arvados.org/main/sdk/python/sdk-python.html), and that Docker is up-to-date and running.

Furthermore, ensure that the user's Arvados environment is up, with the [API tokens configured](https://doc.arvados.org/main/user/reference/api-tokens.html) for the local Arvados instance as well as the Arvados Playground (pirca) where the source data resides. This means that the user can run "`arv-copy`" to move data from Arvados Playground to the local instance.

# Prepare local project

For better organization, create a local project dedicated to this demo, by following the "+NEW" \> "New project" UI elements in WB2. Copy and make note of the new project's UUID. In this guide, we will be using the following one for narrative purposes: `xdemo-j7d0g-n9bd5hxv46diy17`.

# Copy data from pirca to local

For the purpose of demo, the input data has been limited to one sample (i.e. from one UK PGP participant), as a pair of compressed FASTQ files. This data collection UUID on pirca is `pirca-4zz18-57pmwz41p3c6uiw` and the Portable Data Hash is `79e1aab1bac88688a55e19e0dcfb2c7b+41664`. (See [link](https://workbench.pirca.arvadosapi.com/collections/pirca-4zz18-57pmwz41p3c6uiw)).

Another input collection, the reference dataset, has UUID `pirca-4zz18-206mirljpin8ape` and PDH `18657d75efb4afd31a14bb204d073239+13611`.

To copy the data to the local instance (for example, if it is named "`xdemo`"), use the command  
`arv-copy --project-uuid=xdemo-j7d0g-n9bd5hxv46diy17 \`   
  `pirca-4zz18-57pmwz41p3c6uiw`  
`arv-copy --project-uuid=xdemo-j7d0g-n9bd5hxv46diy17 \`  
  `pirca-4zz18-206mirljpin8ape`

# Prepare and submit workflow

The purpose of this step is to obtain the updated code (including CWL documents, scripts, and Docker container build instructions) so that the workflow may run smoothly on our local machine.

For now, clone the forked workflow code repo:  
`git clone https://github.com/zoe-translates/arvados-tutorial`  
`cd arvados-tutorial/WGS-processing`  
`git checkout origin/WGS-processing-tutorial-updates`  
`git switch -c WGS-processing-tutorial-updates`

## Build Docker containers

Pull the recent `arvados/jobs` Docker image to local to ensure it is used as the base image of the bioinformatics tools images to be built now:  
`docker pull arvados/jobs:3.1.0.dev20250314161126`  
`docker tag arvados/jobs:3.1.0.dev20250314161126 arvados/jobs:latest`

Build the container with BWA and samtools:  
`cd docker/bwa_samtools`  
`docker build -t curii/bwa-samtools:latest .`

Build the container for clinvar-report:  
`cd ..`  
`docker build -t curii/clinvar-report:latest .`

Verify that the images are built in the output of `docker images` command.

## Update input parameter YAML file

The purpose of this step is to point the input file location to the limited data collection before submitting the workflow (along with the default input) to Arvados.

Go back to the WGS processing tutorial base directory:  
`cd ..`

Now edit the `yml/wgs-processing-wf.yml` file and look for the block  
`fastqdir:`  
  `class: Directory`  
  `location: keep:a146a06222f9a66b7d141e078fc67660+376237`

Change the PDH for the location of the '`fastqdir`' directory to that of the collection for our single-participant input data:  
  `location: keep:79e1aab1bac88688a55e19e0dcfb2c7b+41664`

## \[Optional\] Update resource hints

The resource hints for the `bwa mem` commandline tool, defined by the CWL file in the repo, asks for 6 cores, which is conservative. Optionally, this can be increased to 12 for the WTR PRO setup described in the beginning of this document.

In `cwl/helper/bwamem-samtools-view.cwl`:  
  `ResourceRequirement:`  
	`ramMin: 30000`  
	`coresMin: 12`

## Submit workflow to local Arvados instance

`arvados-cwl-runner \`  
  `--project-uuid=xdemo-j7d0g-n9bd5hxv46diy17 \`  
  `--create-workflow \`  
  `cwl/wgs-processing-wf.cwl yml/wgs-processing-wf.yml`

# Execute workflow

In Arvados Workbench 2, navigate to our project and locate the workflow registered with Arvados. Run it the usual way – Locating the registered workflow in the project, or select it from "+NEW" \> "Run workflow". It can be run with the default parameters.