#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error

TOKEN = os.environ.get("GITHUB_TOKEN")
TAG = os.environ.get("CIRCLE_TAG")
REPO_USER = os.environ.get("CIRCLE_PROJECT_USERNAME")
REPO_NAME = os.environ.get("CIRCLE_PROJECT_REPONAME")

if not TOKEN:
    print("GITHUB_TOKEN is not set", file=sys.stderr)
    sys.exit(1)
if not TAG:
    print("CIRCLE_TAG is not set; skipping release", file=sys.stderr)
    sys.exit(0)
if not REPO_USER or not REPO_NAME:
    print("Repository information missing", file=sys.stderr)
    sys.exit(1)

repo = f"{REPO_USER}/{REPO_NAME}"
url = f"https://api.github.com/repos/{repo}/releases"

payload = {
    "tag_name": TAG,
    "name": TAG,
    "draft": False,
    "prerelease": False,
}

data = json.dumps(payload).encode()
request = urllib.request.Request(url, data=data,
                                 headers={"Authorization": f"token {TOKEN}",
                                          "Content-Type": "application/json"})
try:
    with urllib.request.urlopen(request) as resp:
        resp_data = json.load(resp)
except urllib.error.HTTPError as exc:
    print(f"Failed to create release: {exc.read().decode()}", file=sys.stderr)
    raise

upload_url = resp_data.get("upload_url", "").split("{")[0]

for path in sys.argv[1:]:
    filename = os.path.basename(path)
    with open(path, "rb") as f:
        file_data = f.read()
    upload_request = urllib.request.Request(
        f"{upload_url}?name={filename}", data=file_data,
        headers={
            "Authorization": f"token {TOKEN}",
            "Content-Type": "application/octet-stream",
        }
    )
    try:
        with urllib.request.urlopen(upload_request) as resp:
            resp.read()
    except urllib.error.HTTPError as exc:
        print(f"Failed to upload {filename}: {exc.read().decode()}", file=sys.stderr)
        raise
