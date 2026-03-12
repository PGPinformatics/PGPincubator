import pathlib
import re

from itertools import count
import time
from urllib.parse import parse_qs, urlsplit

import requests

# Config knobs
# Page size to request
API_TOOLS_PAGE_SIZE = 1000
# Exponential back off starting delay
API_RETRY_DELAY_START = 10
# 7 retries adds up to ~10 minutes total
API_RETRY_COUNT = 7


def fetchToolsIndex():
    tools = []
    # Start max page at 0 for first page, updates on every loop
    max_offset = 0
    # Increment offset by page size until exceeds max_offset
    for offset in count(0, API_TOOLS_PAGE_SIZE):
        if offset > max_offset:
            break
        newTools, lastOffset = fetchToolsIndexPage(offset)
        tools.extend(newTools)
        max_offset = lastOffset
    return tools


class APIRequestException(Exception):
    pass


def fetchToolsIndexPage(offset: int):
    apiToolsUrl = "https://api.biocontainers.pro/ga4gh/trs/v2/tools"
    toolParams = {"sort_field": "id", "sort_order": "asc"}
    retryCount = 0

    while retryCount < API_RETRY_COUNT:
        # Sleep if retrying at beginning for simplicity
        if retryCount > 0:
            print("Sleeping", retrySleep, "seconds before retry")
            time.sleep(retrySleep)

        # Update sleep with 0 indexed count and increment count
        retrySleep = API_RETRY_DELAY_START * pow(2, retryCount)
        retryCount += 1
        try:
            print("Requesting tools index offset", offset, "limit", API_TOOLS_PAGE_SIZE)
            response = requests.get(
                apiToolsUrl,
                {**toolParams, "offset": offset, "limit": API_TOOLS_PAGE_SIZE},
            )
            response.raise_for_status()
            lastPage = response.headers["last_page"]
            lastOffset = int(parse_qs(urlsplit(lastPage).query)["offset"][0])
            print("Last offset set to:", lastOffset)

            return response.json(), lastOffset
        except requests.exceptions.HTTPError as error:
            print("Http Error:", error)
        except Exception as error:
            print("Unknown error:", error)

    # Retry loop finished without success, raise exception
    raise APIRequestException("api retries exhausted without success")


def fetchToolVersion(tool: str, version: str):
    versionUrl = "https://api.biocontainers.pro/ga4gh/trs/v2/tools/%s/versions/%s" % (
        tool,
        version,
    )
    retryCount = 0

    while retryCount < API_RETRY_COUNT:
        # Sleep if retrying at beginning for simplicity
        if retryCount > 0:
            print("Sleeping", retrySleep, "seconds before retry")
            time.sleep(retrySleep)

        # Update sleep with 0 indexed count and increment count
        retrySleep = API_RETRY_DELAY_START * pow(2, retryCount)
        retryCount += 1
        try:
            response = requests.get(
                versionUrl,
            )
            response.raise_for_status()

            return response.json()
        # These errors are retried, don't raise but only warn
        except requests.exceptions.HTTPError as error:
            print("Http Error:", error)
        except Exception as error:
            print("Unknown error:", error)

    # Retry loop finished without success, raise exception
    raise APIRequestException("api retries exhausted without success")


class InvalidNameException(Exception):
    pass


# Attempts to create the specified config dir
def createDataDir(name: str):
    path = pathlib.Path(name)
    pathlib.Path.mkdir(path, parents=False, exist_ok=True)
    return path


# Get tool dir, optionally create if not exists
def getToolDir(dataPath: pathlib.Path, toolName: str, create: bool):
    if re.search(r"[/\\]", toolName):
        raise InvalidNameException(
            "tool name cannot contain special characters: " + toolName
        )
    path = pathlib.Path(dataPath / "tools" / toolName)
    if create:
        pathlib.Path.mkdir(path, parents=True, exist_ok=True)
    return path
