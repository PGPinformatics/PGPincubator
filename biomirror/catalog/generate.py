import argparse
import csv
import json
import pathlib
import sqlite3
from tqdm import tqdm
from utils import FileFetcher

DOI_CSV_URL = "https://pirca-4zz18-zqp877swo8kypyn.collections.pirca.arvadosapi.com/PMID_PMCID_DOI.csv"
DOI_CSV_NAME = "PMID_PMCID_DOI.csv"
CATALOG_DB_FILE = "./dist/catalog.db"

# Set up flags / args
parser = argparse.ArgumentParser(
    prog="generate.py", description="Catalog Generation Script"
)
parser.add_argument(
    "--bc-data",
    type=pathlib.Path,
    help="bcmirror data directory to be imported",
    default="../containers/output",
)
args = parser.parse_args()

con = sqlite3.connect(CATALOG_DB_FILE)
cur = con.cursor()

# Create literature table
cur.execute("CREATE TABLE literature(pmid, pmcid, doi)")
# Create indexes to minimize data transfer to the browser
cur.execute("CREATE INDEX idx_lit_pmid on literature (pmid)")
cur.execute("CREATE INDEX idx_lit_pmcid on literature (pmcid)")
cur.execute("CREATE INDEX idx_lit_doi on literature (doi)")
# Populate literature data
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
# Commit DOIDB data now
con.commit()

# Create tools table
cur.execute("CREATE TABLE tools(id, name, description, license, organization)")
# Create indexes to minimize data transfer to the browser
cur.execute("CREATE INDEX idx_tool_id on tools (id)")
cur.execute("CREATE INDEX idx_tool_name on tools (name)")
cur.execute("CREATE INDEX idx_tool_description on tools (description)")
cur.execute("CREATE INDEX idx_tool_license on tools (license)")
cur.execute("CREATE INDEX idx_tool_organization on tools (organization)")
# Populate tool index data
tools = []
with open(args.bc_data / "index.json", "r", encoding="utf-8") as file:
    tools = json.load(file)
for tool in tools:
    id = tool["id"]
    name = tool.get('name', '')
    description = tool.get('description', '')
    license = tool.get('license', '')
    organization = tool.get('organization', '')

    cur.execute("""
        INSERT INTO tools VALUES
            (?, ?, ?, ?, ?)
    """, (id, name, description, license, organization))
# Commit tools table
con.commit()

con.close()
