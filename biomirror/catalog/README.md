# Catalog

This part of the BioMirror project ingests data from other BioMirror tools as well as additional external sources into a single browseable catalog.

## Running the Catalog Generation Script

1. Run BCMirror to create an tools archive
2. Install requirements

    ```bash
    pip install -r requirements.txt
    ```

3. Run the script

    ```bash
    python generate.py --bc-data /path/to/bcdata/output
    ```

The script will download the PMID_PMCID_DOI database and import it into `dist/catalog.db`, with indexing on necessary columns.

The contents of `dist` can then be uploaded to a keep collection or any static file host that supports range requests to allow looking up entries by ID.

## Running as an Arvados workflow

1. Build the catalog-gen container:

    ```bash
    docker build . -t catalog-gen
    ```

2. Upload the workflow and container to an Arvados project

    ```bash
    arvados-cwl-runner --project-uuid zzzzz-j7d0g-000000000000000 --create-workflow catalog-gen.cwl
    ```

    or update an existing workflow:

    ```bash
    arvados-cwl-runner --update-workflow zzzzz-7fd4e-000000000000000 catalog-gen.cwl
    ```

3. Start the workflow providing the bcmirror output as an input to catalog-gen, wait for the catalog output collection to be generated
