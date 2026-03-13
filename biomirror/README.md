# BioMirror

BioMirror is a tool for mirroring and archiving snapshots of the BioContainers API and the containers it references.

## Running the BioMirror script

1. Install python3
2. Install requirements

    ```bash
    pip install -r requirements.txt
    ```

3. Run the script

    ```bash
    python biomirror.py
    ```

The script will archive the main tools index data to `output/index.json` and each tool's version data in `output/tools/tool-name/versions.json`.

## Running as an Arvados workflow

1. Build the biomirror container:

    ```bash
    docker build . -t biomirror
    ```

2. Upload the workflow and container to an Arvados project

    ```bash
    arvados-cwl-runner --project-uuid zzzzz-j7d0g-000000000000000 --create-workflow biomirror.cwl
    ```

    or update an existing workflow:

    ```bash
    arvados-cwl-runner --update-workflow zzzzz-7fd4e-000000000000000 biomirror.cwl
    ```

3. Start the workflow and wait for the output collection to be generated
