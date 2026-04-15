import requests
from tqdm import tqdm

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
                for chunk in tqdm(response.iter_content(chunk_size=chunkSize), total=contentLength / chunkSize, desc="Download", disable=None):
                    file.write(chunk)
            self.file = open(self.filename, mode="r", encoding="utf-8")

        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
