#!/usr/bin/env python3
"""Refresh a PS5 Payload Manager catalog from Codex-PS5 GitHub releases."""

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SOURCE_REPO = "Portablelle/Codex-PS5"
SOURCE_RELEASES_API = f"https://api.github.com/repos/{SOURCE_REPO}/releases?per_page=100"
ASSET_NAME = "assistant-service.elf"
CATALOG_PATH = Path(__file__).resolve().parent / "payloads.json"


def fetch_releases():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "codex-ps5-payload-feed"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(SOURCE_RELEASES_API, headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not read upstream GitHub releases: {exc}") from exc
    if not isinstance(data, list):
        raise RuntimeError("Unexpected GitHub releases response (expected a list)")
    return data


def latest_standalone_elf(releases):
    """Ignore portal archives; find newest published release with standalone ELF."""
    matches = []
    for release in releases:
        if release.get("draft"):
            continue
        for asset in release.get("assets") or []:
            if asset.get("name") == ASSET_NAME and asset.get("browser_download_url"):
                matches.append((release.get("published_at") or release.get("created_at") or "", release, asset))
                break
    if not matches:
        raise RuntimeError("No standalone assistant-service.elf release was found; preserving current feed")
    _, release, asset = max(matches, key=lambda match: match[0])
    return release, asset


def build_catalog(release, asset):
    payload = {
        "name": "assistant-service",
        "filename": ASSET_NAME,
        "url": asset["browser_download_url"],
        "description": "Codex PS5 assistant service ELF. Update the matching ShadowMount app folder separately.",
        "version": release["tag_name"],
        "category": "Utilities",
    }
    digest = asset.get("digest", "")
    if digest.startswith("sha256:") and len(digest) == 71:
        sha256 = digest.removeprefix("sha256:")
        if all(character in "0123456789abcdefABCDEF" for character in sha256):
            payload["checksum"] = sha256.lower()
    return {"name": "Codex PS5 Releases", "payloads": [payload]}


def main():
    releases = fetch_releases()
    release, asset = latest_standalone_elf(releases)
    catalog = build_catalog(release, asset)
    proposed = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    existing = CATALOG_PATH.read_text(encoding="utf-8") if CATALOG_PATH.exists() else None
    if existing == proposed:
        print(f"Already current: {release['tag_name']}")
        return
    CATALOG_PATH.write_text(proposed, encoding="utf-8")
    print(f"Updated to {release['tag_name']}: {asset['browser_download_url']}")


if __name__ == "__main__":
    main()
