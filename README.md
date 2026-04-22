# WCPOS Extensions Catalog

This repository contains the public catalog metadata for WCPOS extensions.

It powers extension discovery, installs, and updates in WCPOS, using `catalog.json` for extension metadata and GitHub Releases for downloadable plugin assets.

## Documentation

- User and developer docs: https://docs.wcpos.com/extensions/
- Catalog landing page: https://docs.wcpos.com/extensions/
- Live catalog file: [`catalog.json`](./catalog.json)

## For Users

If you are looking for install guides, compatibility notes, or extension-specific documentation, start with the WCPOS Extensions docs:

- https://docs.wcpos.com/extensions/

From there you can browse available extensions, read setup instructions, and find links to each extension repository.

## For Developers

To list an extension in the WCPOS catalog:

1. Build your extension as a standard WordPress plugin.
2. Publish releases on GitHub with a version tag and downloadable plugin zip asset.
3. Add or update the extension entry in [`catalog.json`](./catalog.json).
4. Add an icon in [`icons/`](./icons) if needed.
5. Open a pull request to this repository.

For the full catalog schema, release conventions, and submission guidance, use the canonical docs:

- https://docs.wcpos.com/extensions/

## Repository Structure

- [`catalog.json`](./catalog.json) — extension metadata consumed by WCPOS
- [`icons/`](./icons) — icons referenced by catalog entries
- [`scripts/sync_catalog.py`](./scripts/sync_catalog.py) — syncs release metadata from GitHub
- [`tests/`](./tests) — tests for catalog sync logic

## Release Notes

This repository does not ship extension code itself. Each listed extension is versioned and distributed from its own GitHub repository using GitHub Releases.

## Contributing

Issues and pull requests are welcome for catalog updates, metadata fixes, icon changes, and documentation improvements.
