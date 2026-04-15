
import os
import pathlib
import sqlite3
import tempfile
import requests
from tqdm import tqdm

UNTAP_DB_URL = "https://collections.ac2it.arvadosapi.com/c=eddaf802f9f889014e20743c510eb62c-3577/_/arv-stage/untap.db"
UNTAP_DB_PATH = pathlib.Path(tempfile.gettempdir()) / "untap.db"
OUT_FILE = pathlib.Path(os.path.dirname(__file__)) / "untap-ids.txt"

# Download untap DB
response = requests.get(UNTAP_DB_URL, stream=True)
with open(UNTAP_DB_PATH, mode="wb") as file:
    contentLengthHeader = response.headers.get("Content-Length")
    contentLength = 0
    chunkSize = 10 * 1024
    if contentLengthHeader is not None:
        contentLength = int(contentLengthHeader)
    for chunk in tqdm(response.iter_content(chunk_size=chunkSize), total=contentLength / chunkSize, desc="Download", disable=None):
        file.write(chunk)

# Open DB and get cursor
con = sqlite3.connect(UNTAP_DB_PATH)
cur = con.cursor()

cur.execute("SELECT * FROM enrollment_date")
count = 0
try:
    with open(OUT_FILE, "x") as file:
        for row in cur:
            file.write(str(row[1]) + "\n")
            count += 1
except FileExistsError:
    print("Error: untap-ids.txt already exists")
    exit(1)

print("Wrote", count, "entries to untap-ids.txt")
