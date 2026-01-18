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

When upstream releases a new version:

1. Update `version` field in manifest
2. CI will verify it matches PyPI
