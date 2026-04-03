#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool

hints:
  DockerRequirement:
    dockerPull: catalog-gen
    # Dockerfile won't work unless we include the project files too
    # dockerFile: {$include: Dockerfile}
  ResourceRequirement:
    ramMin: 2000
    coresMin: 2

doc: "Generates the hGram metadata catalog"
baseCommand: python
arguments: ["-u", "/app/catalog/generate.py", "--out-dir", $(runtime.outdir)]

requirements:
  NetworkAccess:
     networkAccess: true

inputs:
  bc_data:
    type: Directory
    label: "BCMirror Data"
    doc: "Tool data from the BCMirror tool"
    inputBinding:
      prefix: --bc-data
      position: 1

outputs:
  database:
    type: File
    outputBinding:
      glob: catalog.db
  browser:
    type: File
    outputBinding:
      glob: index.html
  browser-script:
    type: File
    outputBinding:
      glob: index.js
