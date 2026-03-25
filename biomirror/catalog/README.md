# Catalog

This part of the BioMirror project ingests data from other BioMirror tools as well as additional external sources into a single browseable catalog.

## Running the Catalog Generation Script

1. Install python3
2. Install requirements

    ```bash
    pip install -r requirements.txt
    ```

3. Run the script

    ```bash
    python generate.py
    ```

The script will download the PMID_PMCID_DOI database and import it into `dist/catalog.db`, with indexing on necessary columns.

The contents of `dist` can then be uploaded to a keep collection or any static file host that supports range requests to allow looking up entries by ID.
