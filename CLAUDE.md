# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Scoop bucket (Windows package manager) for Python Ankara community tools. It mirrors [homebrew-tap](https://github.com/python-ankara-toplulugu/homebrew-tap) for Windows users.

## Architecture

Packages use **pipx** for installation rather than direct downloads:

- `bucket/*.json` - Scoop manifests that depend on pipx
- `scripts/noop.ps1` - Placeholder file (Scoop requires a URL, but pipx handles actual install)
- Manifests use `checkver.jsonpath` to auto-detect new versions from PyPI

## Adding a New Package

1. Copy the template from CONTRIBUTING.md
2. Create `bucket/<package-name>.json`
3. Replace placeholders with package info from PyPI
4. Update README.md package table

The hash `fdcbbea851292d9aa67f598bc6f1ab96e58873385972cd3d209ccab239cbad87` is for `scripts/noop.ps1` - reuse it for all pipx-based packages.

## CI/CD

GitHub Actions runs on every PR:

- **lint**: Validates JSON syntax
- **test**: Installs package on Windows and runs `--help`/`--version`
- **checkver**: Compares manifest version against PyPI (warns on mismatch)

## Version Updates

Two automated workflows handle version updates (mirroring homebrew-tap):

**Polling** (`update-manifests.yml`):

- Runs weekly on Mondays at 9:00 UTC
- Checks all packages against PyPI
- Creates a PR if updates are found
- Supports `--package` input to target a specific package
- Supports `--dry_run` to check without creating PR

**Push-based** (`update-manifest-dispatch.yml`):

- Triggered via `repository_dispatch` from package repos
- Instant updates after PyPI publish
- Package repos can trigger with:
  ```bash
  curl -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/repos/python-ankara-toplulugu/scoop-bucket/dispatches \
    -d '{"event_type":"update-manifest","client_payload":{"package":"ossin"}}'
  ```

**Manual**: Trigger the update-manifests workflow from GitHub Actions, or update the `version` field in manifest directly.
