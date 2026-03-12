import argparse
import json
import pathlib
from utils import fetchToolVersion, fetchToolsIndex, createDataDir, getToolDir


# Set up flags / args
parser = argparse.ArgumentParser(
    prog="biomirror.py", description="BioContainers Mirror Script"
)
parser.add_argument(
    "--out-dir",
    type=createDataDir,
    help="output directory for saved data",
    default="output",
)
parser.add_argument(
    "--verify",
    action="store_true",
    help="verifies existing data instead of fetching new data",
)
parser.add_argument(
    "--fetch-limit",
    type=int,
    help="limits fetched versions to n tools for testing",
)
args = parser.parse_args()

# Print something out before any work starts so we can verify it has started
print("Starting biomirror...")

if args.fetch_limit is not None:
    print("Warning: Using fetch-limit for debug produces partial archives!")

# Update tool index
tools = []  # Array of tools from index
indexPath: pathlib.Path = args.out_dir / "index.json"
if args.verify:
    # Try to read existing tools index
    with open(indexPath, "r", encoding="utf-8") as file:
        tools = json.load(file)
    print("Loaded", len(tools), "tools from index.json")
else:
    # Fetch all tools
    tools = fetchToolsIndex()
    # Print some stats
    print("Fetched", len(tools), "tools from API")
    # Write tools to json
    with open(indexPath, "w", encoding="utf-8") as file:
        json.dump(tools, file, ensure_ascii=False, indent=2)

# Update tool versions
toolVersions = {}  # Dict of tool_id to version array
skipped: set[str] = set()
if args.verify:
    for tool in tools:
        tool_id = str(tool["id"])
        try:
            # Try to read existing tools index
            toolDataDir = getToolDir(args.out_dir, tool_id, False)
            with open(toolDataDir / "versions.json", "r", encoding="utf-8") as file:
                toolVersions.update({tool_id: json.load(file)})
        except FileNotFoundError:
            print("Error: versions.json was not found for tool", tool_id)
            skipped.add(tool_id)
        except Exception as error:
            print("Unknown error:", error)
            skipped.add(tool_id)
    print("Loaded", len(toolVersions), "tool versions from output")
else:
    for tool in tools:
        if args.fetch_limit is not None and len(toolVersions) >= args.fetch_limit:
            print("Reached debug fetch-limit, exiting early")
            break
        tool_id = str(tool["id"])
        print("Requesting versions for:", tool_id)
        tool_versions = []
        for tool_version in tool["versions"]:
            tool_version_id = tool_version["id"]
            try:
                version = fetchToolVersion(tool_id, tool_version_id)
                tool_versions.append(version)
            except Exception as err:
                skipped.add(tool_id + "/" + tool_version_id)
                print("Skipping", tool_id + "/" + tool_version_id ,"due to error:", err)
        if len(tool_versions) > 0:
            # Add tool versions to dict
            toolVersions.update({tool_id: tool_versions})
            # Write tool versions to json
            toolDataDir = getToolDir(args.out_dir, tool_id, True)
            with open(toolDataDir / "versions.json", "w", encoding="utf-8") as file:
                json.dump(tool_versions, file, ensure_ascii=False, indent=2)
        else:
            print("No versions loaded for", tool_id, ": skipping file write")

# We have tools and toolVersions, do some stats
totalVersions = 0
totalDockerBytes = 0
totalDockerImages = 0
totalCondaImages = 0
totalSingularityBytes = 0
totalSingularityImages = 0

skippedStats: set[str] = set()
for tool in tools:
    try:
        for version in toolVersions[tool["id"]]:
            totalVersions += 1
            for image in version["images"]:
                if image["image_type"] == "Docker":
                    totalDockerImages += 1
                    totalDockerBytes += int(image["size"])
                if image["image_type"] == "Conda":
                    totalCondaImages += 1
                if image["image_type"] == "Singularity":
                    totalSingularityImages += 1
                    totalSingularityBytes += int(image["size"])
    except:
        skippedStats.add(tool["id"])


print("\nIntegrity Check:\n----------------")
if len(tools) != len(toolVersions):
    print("[!!] Different number of tools in index vs version list")
else:
    print("[OK] Same number of tools in index vs version list")
if len(skipped) > 0:
    print("[!!]", len(skipped), "tool versions failed to load from API or disk")
else:
    print("[OK] No tool versions failed to load")
if len(skippedStats) > 0:
    if args.fetch_limit is not None:
        print("[!!]", len(skippedStats), "tools not processed for stats due to fetch-limit, stats may be incomplete")
    else:
        print("[!!]", len(skippedStats), "tools missing from versions data when processing stats")
else:
    print("[OK] All tools processed for stats")

print("\nStats:\n------")
print("Tools:", len(tools))
print("Versions:", totalVersions)
print("Docker Images:", totalDockerImages)
print(
    "Docker Size:",
    str(round(totalDockerBytes / (1000 * 1000 * 1000 * 1000), 2)),
    "TB",
)
print("Conda Images:", totalCondaImages)
print("Singularity Images:", totalSingularityImages)
print(
    "Singularity Size:",
    str(round(totalSingularityBytes / (1000 * 1000 * 1000 * 1000), 2)),
    "TB",
)
