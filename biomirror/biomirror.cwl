#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool

hints:
  DockerRequirement:
    dockerPull: biomirror
    # Dockerfile won't work unless we include the project files too
    # dockerFile: {$include: Dockerfile}
  ResourceRequirement:
    ramMin: 2000
    coresMin: 2

doc: "Mirrors BioContainers API metadata into a collection"
baseCommand: python
arguments: ["-u", "/app/biomirror/biomirror.py", "--out-dir", $(runtime.outdir)/output]

requirements:
  NetworkAccess:
     networkAccess: true

inputs:
  skipIndexUpdate:
    type: boolean?
    label: "Skip index update"
    doc: "Load tool index from disk instead of API"
    inputBinding:
      position: 1
      prefix: "--skip-index-update"
  skipVersionUpdate:
    type: boolean?
    label: "Skip version update"
    doc: "Load tool versions from disk instead of API"
    inputBinding:
      position: 2
      prefix: "--skip-version-update"

outputs:
  output:
    type: Directory
    outputBinding:
      glob: $(runtime.outdir)/output/
