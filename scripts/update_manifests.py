#!/usr/bin/env python3
"""Update the pipx-shim Scoop manifests in ``bucket/`` from PyPI.

Every manifest in this bucket is a pipx shim: its ``url`` is the static
``scripts/noop.ps1`` (so the hash never changes) and the only thing that moves on
a release is ``version``. Each manifest declares where to look via ``checkver``:

    "checkver": {"url": "https://pypi.org/pypi/<pkg>/json", "jsonpath": "$.info.version"}

This script reads that, fetches the latest version, and bumps ``version`` in
place when PyPI is ahead. It never commits — the calling workflow opens the PR
from the resulting diff.

PyPI's ``$.info.version`` reports the highest *non-yanked* release, so it can
move backward when a release is yanked. This script refuses to roll a manifest
backward: a lower version is reported as a ``::warning::`` and skipped.

Usage::

    python scripts/update_manifests.py            # check every manifest
    python scripts/update_manifests.py ossin      # only bucket/ossin.json
    python scripts/update_manifests.py --dry-run   # report, do not write

Prints a Markdown summary of what changed (consumed as the PR body) and exits 0
whether or not anything changed; nonzero only if a manifest fails to update (the
rest are still attempted).
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

BUCKET = Path(__file__).resolve().parent.parent / "bucket"
_UA = "scoop-bucket-updater"


def _get_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": _UA, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            return json.load(resp)
    except Exception as exc:  # noqa: BLE001 — re-raise with the URL for context
        raise RuntimeError(f"fetching {url}: {exc}") from exc


def _resolve(data: dict, jsonpath: str) -> str:
    """Resolve a simple ``$.a.b`` dotted JSONPath against ``data``."""
    node: object = data
    for key in jsonpath.removeprefix("$").strip(".").split("."):
        try:
            node = node[key]  # type: ignore[index]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"jsonpath {jsonpath!r} did not resolve: {exc}") from exc
    if not isinstance(node, (str, int, float)):
        raise ValueError(
            f"jsonpath {jsonpath!r} resolved to a non-scalar {type(node).__name__}"
        )
    return str(node)


def _latest(checkver: dict) -> str:
    return _resolve(_get_json(checkver["url"]), checkver.get("jsonpath", "$.info.version"))


def _release_tuple(version: str) -> tuple[int, ...]:
    """The leading numeric release of a version, e.g. ``1.2.3rc1`` -> ``(1, 2, 3)``."""
    match = re.match(r"\d+(?:\.\d+)*", version)
    return tuple(int(part) for part in match.group(0).split(".")) if match else ()


def _is_downgrade(latest: str, current: str) -> bool:
    """True only when ``latest`` is unambiguously an older release than ``current``.

    Compares the numeric release tuples (padded to equal length). Returns False
    when either side has no parseable release, so anything ambiguous is left to
    proceed and be caught in PR review rather than silently skipped.
    """
    latest_tuple, current_tuple = _release_tuple(latest), _release_tuple(current)
    if not latest_tuple or not current_tuple:
        return False
    width = max(len(latest_tuple), len(current_tuple))
    latest_tuple += (0,) * (width - len(latest_tuple))
    current_tuple += (0,) * (width - len(current_tuple))
    return latest_tuple < current_tuple


def _update_manifest(path: Path, *, dry_run: bool) -> str | None:
    """Bump one manifest's version; return a ``"old → new"`` note or None."""
    data = json.loads(path.read_text(encoding="utf-8"))
    checkver = data.get("checkver")
    if not checkver or "url" not in checkver:
        print(f"::warning::{path.name}: no checkver.url, skipping", file=sys.stderr)
        return None
    if "version" not in data:
        raise KeyError(f"{path.name}: manifest has no 'version' field")

    current = data["version"]
    latest = _latest(checkver)
    if latest == current:
        return None
    if _is_downgrade(latest, current):
        print(
            f"::warning::{path.name}: PyPI reports a lower version "
            f"({latest} < {current}); possible yank, skipping",
            file=sys.stderr,
        )
        return None

    if not dry_run:
        data["version"] = latest
        path.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
    return f"`{current}` → `{latest}`"


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    targets = [a for a in argv if not a.startswith("-")]

    changes: dict[str, str] = {}
    failures: dict[str, str] = {}
    for path in sorted(BUCKET.glob("*.json")):
        if targets and path.stem not in targets:
            continue
        try:
            note = _update_manifest(path, dry_run=dry_run)
        except Exception as exc:  # noqa: BLE001 — surface any source/network error loudly
            print(f"::error::{path.name}: {exc}", file=sys.stderr)
            failures[path.stem] = str(exc)
            continue
        if note:
            changes[path.stem] = note

    if changes:
        for name, note in changes.items():
            print(f"- **{name}**: {note}")
    else:
        print("No updates available.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
