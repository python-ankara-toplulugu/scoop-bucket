#!/usr/bin/env python3
"""Update the pipx-shim Scoop manifests in ``bucket/`` from PyPI.

Every manifest in this bucket is a pipx shim: its ``url`` is the static
``scripts/noop.ps1`` (so the hash never changes) and the only thing that moves on
a release is ``version``. Each manifest declares where to look via ``checkver``:

    "checkver": {"url": "https://pypi.org/pypi/<pkg>/json", "jsonpath": "$.info.version"}

This script reads that, fetches the latest version, and bumps ``version`` in
place when it differs. It never commits — ``peter-evans/create-pull-request``
opens the PR from the resulting diff.

Usage::

    python scripts/update_manifests.py            # check every manifest
    python scripts/update_manifests.py ossin      # only bucket/ossin.json
    python scripts/update_manifests.py --dry-run   # report, do not write

Prints a Markdown summary of what changed (consumed as the PR body) and exits 0
whether or not anything changed; nonzero only on error.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

BUCKET = Path(__file__).resolve().parent.parent / "bucket"
_UA = "scoop-bucket-updater"


def _get_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": _UA, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        return json.load(resp)


def _resolve(data: dict, jsonpath: str) -> str:
    """Resolve a simple ``$.a.b`` dotted JSONPath against ``data``."""
    node: object = data
    for key in jsonpath.removeprefix("$").strip(".").split("."):
        node = node[key]  # type: ignore[index]
    return str(node)


def _latest(checkver: dict) -> str:
    return _resolve(_get_json(checkver["url"]), checkver.get("jsonpath", "$.info.version"))


def _update_manifest(path: Path, *, dry_run: bool) -> str | None:
    """Bump one manifest's version; return a ``"old → new"`` note or None."""
    data = json.loads(path.read_text(encoding="utf-8"))
    checkver = data.get("checkver")
    if not checkver or "url" not in checkver:
        print(f"::warning::{path.name}: no checkver.url, skipping", file=sys.stderr)
        return None

    current = data["version"]
    latest = _latest(checkver)
    if latest == current:
        return None

    if not dry_run:
        data["version"] = latest
        path.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
    return f"`{current}` → `{latest}`"


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    targets = [a for a in argv if not a.startswith("-")]

    changes: dict[str, str] = {}
    for path in sorted(BUCKET.glob("*.json")):
        if targets and path.stem not in targets:
            continue
        try:
            note = _update_manifest(path, dry_run=dry_run)
        except Exception as exc:  # noqa: BLE001 — surface any source/network error loudly
            print(f"::error::{path.name}: {exc}", file=sys.stderr)
            return 1
        if note:
            changes[path.stem] = note

    if changes:
        for name, note in changes.items():
            print(f"- **{name}**: {note}")
    else:
        print("No updates available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
