#!/usr/bin/env python3
"""Sync extension catalog versions from GitHub releases."""

from __future__ import annotations

import argparse
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


GITHUB_API_BASE = "https://api.github.com"


def parse_github_repo(homepage_url: str) -> tuple[str, str]:
    parsed = urlparse(homepage_url)
    if parsed.netloc.lower() != "github.com":
        raise ValueError(f"Homepage is not a github.com URL: {homepage_url}")

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise ValueError(f"Homepage URL does not include owner/repo: {homepage_url}")

    return parts[0], parts[1]


def normalize_version(tag_name: str) -> str:
    if tag_name.startswith("v"):
        return tag_name[1:]
    return tag_name


def select_download_url(release: dict[str, Any], slug: str, current_url: str) -> str:
    assets = release.get("assets") or []
    expected_name = f"{slug}.zip"

    for asset in assets:
        if asset.get("name") == expected_name and asset.get("browser_download_url"):
            return asset["browser_download_url"]

    for asset in assets:
        name = asset.get("name") or ""
        if name.endswith(".zip") and asset.get("browser_download_url"):
            return asset["browser_download_url"]

    return current_url


def apply_release(entry: dict[str, Any], release: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    updated = deepcopy(entry)

    tag_name = release.get("tag_name")
    if not tag_name:
        return updated, False

    version = normalize_version(tag_name)
    updated["version"] = version
    updated["latest_version"] = version

    published_at = release.get("published_at") or release.get("created_at")
    if published_at:
        updated["released_at"] = published_at

    updated["download_url"] = select_download_url(
        release,
        slug=entry.get("slug", ""),
        current_url=entry.get("download_url", ""),
    )

    return updated, updated != entry


def fetch_latest_release(owner: str, repo: str, token: str | None = None) -> dict[str, Any] | None:
    endpoint = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases/latest"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "wcpos-extensions-catalog-sync",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(endpoint, headers=headers)

    try:
        with urlopen(request, timeout=20) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return None
        raise
    except URLError:
        raise


def sync_catalog_entries(entries: list[dict[str, Any]], token: str | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    updated_entries: list[dict[str, Any]] = []
    changed_slugs: list[str] = []

    for entry in entries:
        homepage = entry.get("homepage", "")
        slug = entry.get("slug", "<unknown>")

        if not homepage:
            updated_entries.append(entry)
            continue

        try:
            owner, repo = parse_github_repo(homepage)
            release = fetch_latest_release(owner, repo, token=token)
        except Exception as error:
            print(f"warning: failed to fetch release for {slug}: {error}", file=sys.stderr)
            updated_entries.append(entry)
            continue

        if not release:
            updated_entries.append(entry)
            continue

        updated, changed = apply_release(entry, release)
        if changed:
            changed_slugs.append(slug)
        updated_entries.append(updated)

    return updated_entries, changed_slugs


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync catalog.json with latest GitHub releases.")
    parser.add_argument("--catalog", default="catalog.json", help="Path to catalog JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    entries = json.loads(catalog_path.read_text(encoding="utf-8"))

    token = os.getenv("GITHUB_TOKEN")
    updated_entries, changed_slugs = sync_catalog_entries(entries, token=token)

    if not changed_slugs:
        print("catalog is already up to date")
        return 0

    if args.dry_run:
        print("catalog updates available for:", ", ".join(changed_slugs))
        return 1

    catalog_path.write_text(f"{json.dumps(updated_entries, indent=2)}\n", encoding="utf-8")
    print("updated catalog entries:", ", ".join(changed_slugs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
