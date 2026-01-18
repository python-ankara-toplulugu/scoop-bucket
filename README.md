# Python Ankara Scoop Bucket

A [Scoop](https://scoop.sh/) bucket for Windows users to install tools from Python Ankara community.

This is the Windows equivalent of our [Homebrew tap](https://github.com/python-ankara-toplulugu/homebrew-tap) for macOS/Linux users.

## Installation

First, install [Scoop](https://scoop.sh/) if you haven't already:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

Then add this bucket:

```powershell
scoop bucket add python-ankara-toplulugu https://github.com/python-ankara-toplulugu/scoop-bucket
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
