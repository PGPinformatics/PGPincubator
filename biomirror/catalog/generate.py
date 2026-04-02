import argparse
import csv
import json
import os
import pathlib
import shutil
import sqlite3
from tqdm import tqdm
from utils import FileFetcher

DOI_CSV_URL = "https://pirca-4zz18-zqp877swo8kypyn.collections.pirca.arvadosapi.com/PMID_PMCID_DOI.csv"
DOI_CSV_FILENAME = "PMID_PMCID_DOI.csv"
CATALOG_DB_FILENAME = "catalog.db"
DIST_DIR = "./dist"

# Set up flags / args
parser = argparse.ArgumentParser(
    prog="generate.py", description="Catalog Generation Script"
)
parser.add_argument(
    "--bc-data",
    type=pathlib.Path,
    help="bcmirror data directory to be imported",
    default="../bcmirror/output",
)
parser.add_argument(
    "--out-dir",
    type=pathlib.Path,
    help="Output directory for database and dist files",
    default=DIST_DIR,
)
parser.add_argument(
    "--force",
    action="store_true",
    help="automatically overwrites existing sqlite DB",
)
args = parser.parse_args()

# Check for tools index before proceeding
indexPath: pathlib.Path = args.bc_data / "index.json"
if not indexPath.exists():
    print("BioContainer mirror data not found. Please provide the directory containing index.json and tools folder using --bc-data")
    exit(1)
# Check for existing db before proceeding
# Do this last to avoid deleting the DB if other prerequisites aren't met
catalogDbPath: pathlib.Path = args.out_dir / CATALOG_DB_FILENAME
if pathlib.Path(catalogDbPath).exists():
    if args.force:
        print("Force flag specified, removing existing DB")
        pathlib.Path(catalogDbPath).unlink()
    else:
        print("Existing DB found, please move or remove it before proceeding or use --force to overwrite it")
        exit(1)

# Prepare to create DB file
# If out_dir is not dist, copy dist to out_dir
# This is done before generating the DB so that stale DBs in dist don't clobber the new DB
if not os.path.samefile(DIST_DIR, args.out_dir):
    print("Detected out-dir differs from dist folder, copying dist to output...")
    shutil.copytree(DIST_DIR, args.out_dir, dirs_exist_ok=True)

# Create new DB
con = sqlite3.connect(catalogDbPath)
cur = con.cursor()

# Create literature table
cur.execute("CREATE TABLE literature(pmid, pmcid, doi)")
# Create indexes to minimize data transfer to the browser
cur.execute("CREATE INDEX idx_lit_pmid on literature (pmid)")
cur.execute("CREATE INDEX idx_lit_pmcid on literature (pmcid)")
cur.execute("CREATE INDEX idx_lit_doi on literature (doi)")
# Populate literature data
with FileFetcher(DOI_CSV_FILENAME, DOI_CSV_URL) as file:
    lineCount = sum(1 for line in file)
    file.seek(0)
    file_reader = csv.reader(file)
    # For all rows
    for i in tqdm(file_reader, total=lineCount, desc="Import", disable=None):
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
with open(indexPath, "r", encoding="utf-8") as file:
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
