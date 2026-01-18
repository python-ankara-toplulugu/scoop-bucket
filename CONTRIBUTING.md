# Contributing to Python Ankara Scoop Bucket

Thanks for your interest in contributing!

## Adding a New Package

### Prerequisites

The package must:
- Be available on [PyPI](https://pypi.org/)
- Be a CLI tool (not a library)
- Be related to Python Ankara community projects

### Steps

1. Create a new JSON manifest in the `bucket/` directory named `<package-name>.json`

2. Use this template for pipx-based packages:

```json
{
    "version": "<version>",
    "description": "<description>",
    "homepage": "<github-url>",
    "license": "<license>",
    "depends": "pipx",
    "url": "https://raw.githubusercontent.com/python-ankara-toplulugu/scoop-bucket/main/scripts/noop.ps1",
    "hash": "fdcbbea851292d9aa67f598bc6f1ab96e58873385972cd3d209ccab239cbad87",
    "installer": {
        "script": "pipx install <package-name>==$version --force"
    },
    "uninstaller": {
        "script": "pipx uninstall <package-name>"
    },
    "checkver": {
        "url": "https://pypi.org/pypi/<package-name>/json",
        "jsonpath": "$.info.version"
    },
    "autoupdate": {
        "url": "https://raw.githubusercontent.com/python-ankara-toplulugu/scoop-bucket/main/scripts/noop.ps1"
    }
}
```

3. Replace all placeholders:
   - `<version>`: Current version on PyPI (e.g., "1.0.0")
   - `<description>`: Brief description of what the tool does
   - `<github-url>`: Homepage URL
   - `<license>`: License identifier (e.g., "MIT", "Apache-2.0")
   - `<package-name>`: The PyPI package name

4. Update `README.md` to include the new package in the table

5. Submit a pull request

### Testing Locally (Windows)

If you have access to a Windows machine:

```powershell
# Add the local bucket
scoop bucket add python-ankara-toplulugu /path/to/this/repo

# Test installation
scoop install python-ankara-toplulugu/<package-name>

# Verify it works
<package-name> --help
```

### Updating a Package Version

When a new version is released on PyPI:

1. Update the `version` field in the manifest
2. The CI will verify the version matches PyPI
3. Submit a PR with the version bump

## Questions?

Open an issue or reach out to the Python Ankara community.
