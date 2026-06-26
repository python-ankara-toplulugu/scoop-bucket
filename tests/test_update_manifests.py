"""Tests for ``scripts/update_manifests.py`` (stdlib ``unittest``, no network).

Run with ``python -m unittest discover tests`` from the repo root.
"""

from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import update_manifests as um  # noqa: E402

SAMPLE = {
    "version": "0.1.0",
    "description": "demo",
    "url": "https://example/noop.ps1",
    "hash": "deadbeef",
    "checkver": {"url": "https://pypi.org/pypi/demo/json", "jsonpath": "$.info.version"},
}


def _write(dir_path: Path, name: str, data: dict) -> Path:
    path = dir_path / f"{name}.json"
    path.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
    return path


class ResolveTest(unittest.TestCase):
    def test_dotted_path(self) -> None:
        self.assertEqual(um._resolve({"info": {"version": "1.2.3"}}, "$.info.version"), "1.2.3")

    def test_missing_key_raises(self) -> None:
        with self.assertRaises(ValueError):
            um._resolve({"info": {}}, "$.info.version")

    def test_non_scalar_raises(self) -> None:
        with self.assertRaises(ValueError):
            um._resolve({"info": {"version": {}}}, "$.info.version")


class DowngradeTest(unittest.TestCase):
    def test_forward_is_not_downgrade(self) -> None:
        self.assertFalse(um._is_downgrade("0.2.0", "0.1.0"))

    def test_lower_is_downgrade(self) -> None:
        self.assertTrue(um._is_downgrade("0.1.0", "0.2.0"))

    def test_padding(self) -> None:
        self.assertFalse(um._is_downgrade("1.2", "1.2.0"))

    def test_unparseable_proceeds(self) -> None:
        self.assertFalse(um._is_downgrade("weird", "0.1.0"))


class UpdateManifestTest(unittest.TestCase):
    def _bump_to(self, latest: str, *, dry_run: bool = False):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = _write(Path(tmp.name), "demo", SAMPLE)
        with mock.patch.object(um, "_latest", return_value=latest):
            note = um._update_manifest(path, dry_run=dry_run)
        return path, note

    def test_bump_preserves_shape(self) -> None:
        path, note = self._bump_to("0.2.0")
        self.assertEqual(note, "`0.1.0` → `0.2.0`")
        written = json.loads(path.read_text())
        self.assertEqual(written["version"], "0.2.0")
        # every other field and key order is preserved
        self.assertEqual(list(written), list(SAMPLE))
        self.assertEqual({k: written[k] for k in written if k != "version"},
                         {k: SAMPLE[k] for k in SAMPLE if k != "version"})
        self.assertTrue(path.read_text().endswith("}\n"))

    def test_dry_run_does_not_write(self) -> None:
        path, note = self._bump_to("0.2.0", dry_run=True)
        self.assertEqual(note, "`0.1.0` → `0.2.0`")
        self.assertEqual(json.loads(path.read_text())["version"], "0.1.0")

    def test_no_change(self) -> None:
        _, note = self._bump_to("0.1.0")
        self.assertIsNone(note)

    def test_downgrade_skipped(self) -> None:
        path, note = self._bump_to("0.0.9")
        self.assertIsNone(note)
        self.assertEqual(json.loads(path.read_text())["version"], "0.1.0")


class MainTest(unittest.TestCase):
    def _run(self, manifests: dict[str, dict], argv: list[str], latest):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        bucket = Path(tmp.name)
        for name, data in manifests.items():
            _write(bucket, name, data)
        buf = io.StringIO()
        with mock.patch.object(um, "BUCKET", bucket), \
                mock.patch.object(um, "_latest", side_effect=latest), \
                redirect_stdout(buf):
            code = um.main(argv)
        return code, buf.getvalue()

    def test_summary_format(self) -> None:
        code, out = self._run({"demo": SAMPLE}, [], lambda cv: "0.2.0")
        self.assertEqual(code, 0)
        self.assertIn("- **demo**: `0.1.0` → `0.2.0`", out)

    def test_no_updates_message(self) -> None:
        code, out = self._run({"demo": SAMPLE}, [], lambda cv: "0.1.0")
        self.assertEqual(code, 0)
        self.assertIn("No updates available.", out)

    def test_target_filter(self) -> None:
        other = {**SAMPLE, "checkver": {"url": "https://pypi.org/pypi/other/json"}}
        code, out = self._run({"demo": SAMPLE, "other": other}, ["demo"], lambda cv: "0.2.0")
        self.assertEqual(code, 0)
        self.assertIn("demo", out)
        self.assertNotIn("other", out)

    def test_one_failure_does_not_abort_rest(self) -> None:
        def latest(checkver):
            if "boom" in checkver["url"]:
                raise RuntimeError("network down")
            return "0.2.0"

        boom = {**SAMPLE, "checkver": {"url": "https://pypi.org/pypi/boom/json"}}
        code, out = self._run({"aaa": SAMPLE, "boom": boom}, [], latest)
        self.assertEqual(code, 1)  # nonzero because one failed
        self.assertIn("- **aaa**: `0.1.0` → `0.2.0`", out)  # healthy one still bumped


if __name__ == "__main__":
    unittest.main()
