let worker;
const searchForm = document.getElementById('searchForm');
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const litResultsTable = document.getElementById('litResultsTable');
const litResultsBody = document.getElementById('litResultsBody');
const toolResultsTable = document.getElementById('toolResultsTable');
const toolResultsBody = document.getElementById('toolResultsBody');

function setStatus(message, level) {
  const statusBox = document.getElementById('statusBox');
  statusBox.textContent = message;

  switch(level) {
    case "success":
      statusBox.className = "alert py-2 alert-success";
      break;
    case "danger":
      statusBox.className = "alert py-2 alert-danger";
      break;
    case "warning":
      statusBox.className = "alert py-2 alert-warning";
      break;
    case "info":
    default:
      statusBox.className = "alert py-2 alert-info";
      break;
  }
}

async function init() {
  searchButton.disabled = true;
  setStatus("Loading database, please wait...", "info");
    try {
      // Fetch worker cross origin and load from blob
      const workerScriptResponse = await fetch("https://cdn.jsdelivr.net/npm/sql.js-httpvfs@0.8.12/dist/sqlite.worker.js");
      const workerScriptContent = await workerScriptResponse.text();
      const workerUrl = URL.createObjectURL(new Blob([workerScriptContent], { type: "text/javascript" }));
      const wasmUrl = "https://cdn.jsdelivr.net/npm/sql.js-httpvfs@0.8.12/dist/sql-wasm.wasm";

      const config = {
        from: "inline",
        config: {
          serverMode: "full",
          url: (new URL("./catalog.db", window.location.href)).href,
          requestChunkSize: 4096,
        }
      };

      worker = await window.createDbWorker(
        [config],
        workerUrl,
        wasmUrl
      );

      setStatus("Database ready. Enter an ID to search.", "info");
      searchButton.disabled = false;
    } catch (error) {
      console.error("Error initializing database:", error);
      setStatus("Error loading database: " + error.message, "danger");
    }
}

async function doSearch(e) {
  e.preventDefault();
  if (!worker) return;
  const query = searchInput.value.trim();
  if (!query) return;

  // Disable search button for aesthetics,
  // form is disabled while submit is running
  searchButton.disabled = true;
  setStatus("Searching...", "info");
  // Hide tables
  litResultsTable.style.display = "none";
  litResultsBody.innerHTML = "";
  toolResultsTable.style.display = "none";
  toolResultsBody.innerHTML = "";

  try {
    const litResults = await worker.db.query(`SELECT pmid, pmcid, doi FROM literature WHERE pmid = ? OR pmcid = ? OR doi = ?`, [query, query, query]);
    const toolResults = await worker.db.query(`SELECT name, description, license FROM tools WHERE name LIKE ? OR description LIKE ?`, [`%${query}%`, `%${query}%`]);
    const resultCount = (litResults ? litResults.length : 0) + (toolResults ? toolResults.length : 0);

    if (resultCount > 0) {
      setStatus(`Found ${resultCount} result(s).`, "success");

      litResults.forEach(row => {
        const tr = document.createElement('tr');
        const tdPmid = document.createElement('td');
        tdPmid.textContent = row.pmid || '-';
        const tdPmcid = document.createElement('td');
        tdPmcid.textContent = row.pmcid || '-';
        const tdDoi = document.createElement('td');
        tdDoi.textContent = row.doi || '-';
        tr.appendChild(tdPmid);
        tr.appendChild(tdPmcid);
        tr.appendChild(tdDoi);
        litResultsBody.appendChild(tr);
      });
      litResultsTable.style.display = "table";

      toolResults.forEach(row => {
        const tr = document.createElement('tr');
        const tdName = document.createElement('td');
        tdName.textContent = row.name || '-';
        const tdDescription = document.createElement('td');
        tdDescription.textContent = row.description || '-';
        const tdLicense = document.createElement('td');
        tdLicense.textContent = row.license || '-';
        tr.appendChild(tdName);
        tr.appendChild(tdDescription);
        tr.appendChild(tdLicense);
        toolResultsBody.appendChild(tr);
      });
      toolResultsTable.style.display = "table";
    } else {
      setStatus("No results found.", "info");
    }
  } catch (error) {
    console.error("Search error:", error);
    setStatus("Error executing search. See console for details.", "danger");
  } finally {
    searchButton.disabled = false;
  }
}

searchForm.addEventListener("submit", doSearch);

init();
