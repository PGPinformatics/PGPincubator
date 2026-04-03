# literature-tools-catalog

A programmatically created catalog of biomedical knowledge, tools, and materials.

## Project Vision

The goal of this project is to create a comprehensive meta-data catalog of the world's biomedical literature, tools, and materials.
Eventually, this catalog will be expanded to include:
- Relevant AI weights.
- Public and private cohorts of well-consented human beings in which biomedical claims can be validated and biomedical tools can be benchmarked.

## Current Milestone (Phase 1 Pivot)

We are pivoting our architecture away from a fully client-side GitHub Pages deployment (which required tricking the browser into loading partial SQLite databases via HTTP Range requests). The new architecture will be entirely server-backed, orchestrated by a Common Workflow Language (CWL) pipeline, and deployed via an Arvados service container.

This new architecture enables parallelized ingestion of different data domains and simplifies the frontend application.

### The New Architecture Workflow
1. **Parallel Ingestion (Go):** Four separate Go programs ingest data for their respective domains (Literature, AI Weights, Cohorts, and Tools/Materials) and output four individual SQLite databases.
2. **Orchestration (CWL):** A CWL workflow runs the four ingestion steps in parallel. The final step of this workflow launches a Go backend server, taking the four generated `.db` files as inputs.
3. **Backend Service (Go):** The long-running Go server exposes a JSON REST API that queries across all four SQLite databases. It also statically serves the frontend assets.
4. **Frontend UI (HTML/JS):** A unified web interface featuring a single search box that queries the backend API. Results are displayed in four distinct, independently pageable sections representing the four catalog domains.

---

## Parallel Work Tracks & TODOs

To accelerate development, the implementation of this new architecture has been divided into distinct, parallelizable tracks. Additional engineers can pick up tasks from any of the tracks below.

### Track 1: Data Ingestion (Go)
The existing `ingest.go` logic needs to be factored out into four separate ingestion programs that will eventually live in an `ingestion/` directory.

- [x] **TODO:** Rename the current `ingest.go` to `ingestion/ingest_literature.go` and update it to specifically output `literature.db` instead of `catalog.db`.
- [ ] **TODO:** Create a stub Go program `ingestion/ingest_ai_weights.go` that outputs a basic schema for AI Weights.
- [ ] **TODO:** Create a stub Go program `ingestion/ingest_cohorts.go` that outputs a basic schema for Human Cohorts.
- [ ] **TODO:** Create a stub Go program `ingestion/ingest_tools_materials.go` that outputs a basic schema for Tools and Materials.

**Implementation Notes:**
* Created `ingestion/` directory with subdirectories for `literature/`, `ai_weights/`, `cohorts/`, and `tools_materials/`.
* Ran `ingest_literature.go` and its test CSV file to output `literature.db`.
* We might want to expand these basic schemas with more domain-specific columns as more specific datasets are incorporated.

### Track 2: Backend API (Go)
The backend server needs to be built from scratch to mount the generated databases.

- [ ] **TODO:** Create a Go server (`backend/server.go`) that takes the file paths to the four generated SQLite databases as command-line arguments.
- [ ] **TODO:** Expose a REST API endpoint (e.g., `/api/search?q={query}`) that queries all four databases and aggregates the results into a single JSON response.
- [ ] **TODO:** Implement static file serving in the Go backend to host the `frontend/` directory.

### Track 3: Frontend UI (HTML/JS)
The old WebAssembly/sql.js-httpvfs frontend must be completely replaced with a standard API-consuming application.

- [ ] **TODO:** Delete the old frontend artifacts (`index.html`, `sqlite.worker.js`, `sql-wasm.wasm`).
- [ ] **TODO:** Create a new `frontend/index.html` and `frontend/app.js`.
- [ ] **TODO:** Implement a layout with a single, global search input box.
- [ ] **TODO:** Design and implement a 4-part layout (Literature, AI Weights, Cohorts, Tools/Materials) that displays the search results from the backend API, allowing each section to be paged independently.

### Track 4: CWL Orchestration
The pipeline that ties everything together.

- [ ] **TODO:** Write CWL tool wrappers for each of the four Go ingestion scripts.
- [ ] **TODO:** Write a CWL tool wrapper for the `backend/server.go` application.
- [ ] **TODO:** Create the master `workflow/catalog_pipeline.cwl` that executes the four ingestion tools in parallel, and then passes the resulting `.db` files into the backend server tool as the final step.
