# hGram Catalog

A programmatically created catalog of biomedical knowledge, tools, and materials.

## Project Vision

The goal of this project is to create a comprehensive meta-data catalog of the world's biomedical literature, tools, and materials.
Eventually, this catalog will include:

* An index of biocontainer tools and their metadata
* A database of biomedical literature from PMC and PubMed
* Relevant AI weights.
* Public and private cohorts of well-consented human beings in which biomedical claims can be validated and biomedical tools can be benchmarked.

These resources will be aggregated using automated pipelines into a browseable format that can be updated at periodic intervals.

### TODOs

1. Create a single milti-step worflow to run bcmirror and feed the outputs into catalog generate, which should output the contents of `dist` in the output collection
2. Modify generate.py to import additional data into the sqlite database, using arvados URL inputs to abstract away data acquisition

## Full Project Plan

### Phase 1: Foundation and Initial Ingestion

As a starting point, we built a foundation to ingest metadata from the biocontainers API, Europe PMC and PubMed. This data gets ingested into an SQLite database using a python script and uploaded to a static file server along with an html/js page that allows browsing/searching of the catalog.

1. **Data Ingestion**:
   * The BCMirror script archives a copy of tools and tool versions from the biocontainers api into a structure of json files
   * The catalog generator ingests the PMID <> PMCID <> DOI map downloaded from EuropePMC (`PMID_PMCID_DOI.csv`) as well as the bcmirror output
2. **Data Processing and Indexing**:
   * The catalog generator script outputs a well-indexed `catalog.db` optimized for querying.
3. **Frontend Web Interface**:
   * A static web page with JavaScript that loads and queries the SQLite database on-demand using range requests through the library [sql.js-httpvfs](https://github.com/phiresky/sql.js-httpvfs).
   * Enables users to performantly search the catalog entirely client-side, reducing server infrastructure needs.

### Phase ??: Making tools available to Arvados

User story: A user finds a tool in the catalog they would like to try. A link is available that does one of several things:

* Provides a mechanism to load the tool container into arvados from an external source (container repo)
* Brings them to a pre-loaded project with a workflow they can use
* Runs a service container they can access that contains the tool

### Phase ??: Additional Literature Metadata Ingestion

* Expand the ingestion program or create additional scripts to fetch additional metadata (titles, authors, abstracts, publication dates) from Europe PMC and PubMed APIs for the ingested IDs.
* Update the SQLite schema to store and index this enriched metadata.
* Enhance the frontend search capabilities to support text-based searches on titles and abstracts.

### Phase ??: Forming links between catalog facets

* Prerequisite for advanced faceted search
* Define a schema for storing links in sqlite between:
  * Tools/tool versions
  * Literature IDs (PMID, PMCID, DOI)
  * Weights (when added)
  * Cohorts (when added)
* Create a mechanism to add these links to the sqlite database
* Create a UI to search/surface these links

### Phase ??: Advanced Faceted Search

* Improve catalog browser UI for more advanced queries, not just single entry retrieval
* TODO Determine what types of queries across multiple data sets are useful

### Phase ??: AI Weights and Human Cohorts

* Expand the database to catalog relevant AI models and their weights.
* Integrate metadata for public and private human cohorts (ensuring appropriate consent and privacy standards are modeled in the metadata).
* Provide advanced querying to connect literature claims and tool benchmarks to specific human cohorts.
