import importlib.util
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("simple_dev_release", ROOT / "tools" / "release.py")
release = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def test_source_contract(self) -> None:
        report = release.validate_source()
        self.assertTrue(report["ok"], report["errors"])

    def test_build_and_install_simulation(self) -> None:
        build = release.build_release()
        self.assertTrue(build["ok"], build.get("errors"))
        verify = release.verify_release()
        self.assertTrue(verify["ok"], verify.get("errors"))
        self.assertEqual(
            verify["install_simulation"],
            {"openai": True, "claude": True, "generic": True, "vscode": True},
        )

    def test_runtime_archive_excludes_build_tools(self) -> None:
        release.build_release()
        archive_path = ROOT / "dist" / "simple-dev-1.0.0.zip"
        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
        self.assertFalse(any("/tools/" in name for name in names))
        self.assertFalse(any("/.github/" in name for name in names))
        self.assertIn("simple-dev/security/permission_policy.json", names)

    def test_compatibility_archive_excludes_raw_or_nested_evidence(self) -> None:
        release.build_release()
        archive_path = ROOT / "dist" / "simple-dev-1.0.0-compatibility.zip"
        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
        self.assertFalse(any(name.endswith("telemetry_events.jsonl") for name in names))
        self.assertFalse(any("/yao-package/" in name for name in names))
        self.assertFalse(any("/skill_atlas_sources/" in name for name in names))


if __name__ == "__main__":
    unittest.main()
