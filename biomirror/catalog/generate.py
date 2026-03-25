import csv
import sqlite3
import requests
from tqdm import tqdm

DOI_CSV_URL = "https://pirca-4zz18-zqp877swo8kypyn.collections.pirca.arvadosapi.com/PMID_PMCID_DOI.csv"
DOI_CSV_NAME = "PMID_PMCID_DOI.csv"
CATALOG_DB_FILE = "./dist/catalog.db"

# Helper class to read files from disk or fetch them on-demand when needed
class FileFetcher:
    def __init__(self, filename, url):
        self.filename = filename
        self.url = url

    def __enter__(self):
        try:
            self.file = open(self.filename, mode="r", encoding="utf-8")
            print("Info: File found, reading from disk...")
        except FileNotFoundError:
            print("Info: File not found. Downloading...")
            response = requests.get(self.url, stream=True)
            with open(self.filename, mode="wb") as file:
                contentLengthHeader = response.headers.get("Content-Length")
                contentLength = 0
                chunkSize = 10 * 1024
                if contentLengthHeader is not None:
                    contentLength = int(contentLengthHeader)
                for chunk in tqdm(response.iter_content(chunk_size=chunkSize), total=contentLength / chunkSize, desc="Download"):
                    file.write(chunk)
            self.file = open(self.filename, mode="r", encoding="utf-8")

        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()

con = sqlite3.connect(CATALOG_DB_FILE)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS literature(pmid, pmcid, doi)")

# Create indexes to minimize data transfer to the browser
cur.execute("CREATE INDEX idx_lit_pmid on literature (pmid)")
cur.execute("CREATE INDEX idx_lit_pmcid on literature (pmcid)")
cur.execute("CREATE INDEX idx_lit_doi on literature (doi)")

# open file
with FileFetcher(DOI_CSV_NAME, DOI_CSV_URL) as file:
    lineCount = sum(1 for line in file)
    file.seek(0)
    file_reader = csv.reader(file)
    # For all rows
    for i in tqdm(file_reader, total=lineCount, desc="Import"):
        if len(i) == 3:
            cur.execute("""
                INSERT INTO literature VALUES
                    (?, ?, ?)
            """, (i[0], i[1], i[2]))
            # Don't commit between each insertion for speed
        else:
            print("Anomalous row skipped:", i)

# Commit all changes now
con.commit()
con.close()
