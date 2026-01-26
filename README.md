# Python Ankara Scoop Bucket

A [Scoop](https://scoop.sh/) bucket for Windows users to install tools from Python Ankara community.

This is the Windows equivalent of our [Homebrew tap](https://github.com/python-ankara-toplulugu/homebrew-tap) for macOS/Linux users.

## Installation

First, install [Scoop](https://scoop.sh/) if you haven't already:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

Then install packages directly:

```powershell
scoop install python-ankara-toplulugu/ossin
```

Or add the bucket first for easier access:

```powershell
scoop bucket add python-ankara-toplulugu https://github.com/python-ankara-toplulugu/scoop-bucket
scoop install ossin
```

## Available Packages

| Package                                                   | Description                                                      | Install                                       |
| --------------------------------------------------------- | ---------------------------------------------------------------- | --------------------------------------------- |
| [ossin](https://github.com/python-ankara-toplulugu/ossin) | A beautiful system information utility with Rich terminal output | `scoop install python-ankara-toplulugu/ossin` |

## Usage

After installation, you can use ossin directly:

```powershell
# Show system information
ossin

# Show help
ossin --help

# Show version
ossin --version
```

## How It Works

This bucket uses [pipx](https://pipx.pypa.io/) to install Python CLI tools in isolated environments. When you install a package:

1. Scoop automatically installs `pipx` as a dependency
2. The package is installed from PyPI via pipx
3. The CLI command becomes available in your PATH

## Automated Updates

Manifests are kept up-to-date through two complementary workflows:

### Scheduled Updates

The `auto-update.yml` workflow runs weekly on Mondays at 9:00 UTC. It checks all packages against PyPI and creates a PR if updates are found.

### Event-Driven Updates

The `update-manifest-dispatch.yml` workflow receives `repository_dispatch` events from package repositories. This enables instant updates when a new version is published to PyPI.

### Flow

```
[package repo]                    [scoop-bucket]
     │                                  │
     │ Release published                │
     ▼                                  │
  repository_dispatch ─────────────────►│
  (package, version)                    ▼
                            update-manifest-dispatch.yml
                                        │
                                        ▼
                                   Creates PR
```

---

## Setting Up Automatic Updates for Your Package

If you maintain a package in this bucket, you can configure your repository to automatically trigger manifest updates after publishing to PyPI.

<details>
<summary><strong>For Humans</strong></summary>

### Option A: Ask an LLM

If you use an LLM assistant (like Claude, ChatGPT, etc.), you can ask it to set this up for you:

> Set up automatic Scoop bucket updates for my Python package repository. Follow the instructions at: https://github.com/python-ankara-toplulugu/scoop-bucket

### Option B: Manual Setup

1. **Create a GitHub Personal Access Token (PAT)**
   - Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - Create a new token with `repo` scope
   - Copy the token value

2. **Add the token to your package repository**
   - Go to your package repo > Settings > Secrets and variables > Actions
   - Create a new secret named `SCOOP_BUCKET_TOKEN`
   - Paste your PAT as the value

3. **Create the workflow file**
   - Create `.github/workflows/update-scoop-manifest.yml` in your package repository:

```yaml
name: Update Scoop Manifest

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Scoop bucket update
        run: |
          curl -X POST \
            -H "Authorization: token ${{ secrets.SCOOP_BUCKET_TOKEN }}" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/python-ankara-toplulugu/scoop-bucket/dispatches \
            -d '{"event_type":"update-manifest","client_payload":{"package":"YOUR_PACKAGE_NAME"}}'
```

Replace `YOUR_PACKAGE_NAME` with your actual package name (e.g., `ossin`).

</details>

<details>
<summary><strong>For LLM Agents</strong></summary>

### Prerequisites

- Package repository with GitHub Actions enabled
- Write access to create secrets and workflow files
- Package name matching the manifest filename in `bucket/` directory

### Setup Steps

1. **Create a GitHub Personal Access Token**
   - Navigate to https://github.com/settings/tokens
   - Generate new token (classic) with `repo` scope
   - Note: Token will be used to trigger repository_dispatch events

2. **Store the token as a repository secret**
   - In the package repository, go to Settings > Secrets and variables > Actions
   - Create secret: `SCOOP_BUCKET_TOKEN` = `<PAT_VALUE>`

3. **Create the workflow file** at `.github/workflows/update-scoop-manifest.yml`:

```yaml
name: Update Scoop Manifest

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Trigger Scoop bucket update
        env:
          PACKAGE_NAME: "YOUR_PACKAGE_NAME" # Replace with actual package name
        run: |
          curl -X POST \
            -H "Authorization: token ${{ secrets.SCOOP_BUCKET_TOKEN }}" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/python-ankara-toplulugu/scoop-bucket/dispatches \
            -d "{\"event_type\":\"update-manifest\",\"client_payload\":{\"package\":\"$PACKAGE_NAME\"}}"
```

### Payload Schema

```json
{
  "event_type": "update-manifest",
  "client_payload": {
    "package": "string (required) - Package name matching bucket/*.json",
    "version": "string (optional) - Specific version, defaults to latest from PyPI",
    "pypi_name": "string (optional) - PyPI package name if different from package name"
  }
}
```

</details>

---

## Updating Packages

To update a package to the latest version:

```powershell
scoop update ossin
```

## Uninstalling

```powershell
scoop uninstall ossin
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new packages to this bucket.

## License

MIT License - see [LICENSE](LICENSE) for details.
