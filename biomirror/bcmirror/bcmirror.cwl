#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool

hints:
  DockerRequirement:
    dockerPull: bcmirror
    # Dockerfile won't work unless we include the project files too
    # dockerFile: {$include: Dockerfile}
  ResourceRequirement:
    ramMin: 2000
    coresMin: 2

doc: "Mirrors BioContainers API metadata into a collection"
baseCommand: python
arguments: ["-u", "/app/bcmirror/bcmirror.py", "--out-dir", $(runtime.outdir)]

requirements:
  NetworkAccess:
     networkAccess: true

inputs:
  verify:
    type: boolean?
    label: "Verify data"
    doc: "Verifies existing data instead of fetching new data"
    inputBinding:
      position: 1
      prefix: "--verify"
  fetchLimit:
    type: int?
    label: "Limit fetches"
    doc: "Limits fetched versions to n tools for testing"
    inputBinding:
      position: 2
      prefix: "--fetch-limit"

outputs:
  index:
    type: File
    outputBinding:
      glob: index.json
  tools:
    type: Directory
    outputBinding:
      glob: tools
