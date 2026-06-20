#!/usr/bin/env python3
"""Validate, build, and verify simple-dev release artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import yaml


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
TARGETS = ["openai", "claude", "generic", "vscode"]
DECLARED_TARGETS = ["openai", "claude", "generic", "agent-skills-compatible", "vscode"]
RUNTIME_ENTRIES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "manifest.json",
    "agents",
    "evals",
    "security",
    "skill-ir",
]
EVIDENCE_EXCLUDES = {"telemetry_events.jsonl", "yao-package", "skill_atlas_sources"}
REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "manifest.json",
    "agents/interface.yaml",
    "agents/openai.yaml",
    "evals/semantic_config.json",
    "evals/trigger_cases.json",
    "evals/output/cases.jsonl",
    "evals/packaging_expectations.json",
    "skill-ir/examples/simple-dev.json",
]
REQUIRED_GATE_REPORTS = [
    "compiled_targets.json",
    "output_quality_scorecard.json",
    "output_execution_runs.json",
    "conformance_matrix.json",
    "security_trust_report.json",
    "package_verification.json",
    "install_simulation.json",
    "runtime_permission_probes.json",
    "registry_audit.json",
    "upgrade_check.json",
    "adoption_drift_report.json",
    "review_waivers.json",
    "review-studio.json",
]
INSTALL_CONTRACTS = {
    "openai": {
        "user_paths": ["~/.agents/skills/simple-dev"],
        "project_paths": [".agents/skills/simple-dev"],
        "invocation": "$simple-dev",
    },
    "claude": {
        "user_paths": ["~/.claude/skills/simple-dev"],
        "project_paths": [".claude/skills/simple-dev"],
        "invocation": "/simple-dev",
    },
    "generic": {
        "user_paths": [],
        "project_paths": ["<client-skill-root>/simple-dev"],
        "invocation": "client-defined",
    },
    "vscode": {
        "user_paths": [
            "~/.copilot/skills/simple-dev",
            "~/.claude/skills/simple-dev",
            "~/.agents/skills/simple-dev",
        ],
        "project_paths": [
            ".github/skills/simple-dev",
            ".claude/skills/simple-dev",
            ".agents/skills/simple-dev",
        ],
        "invocation": "/simple-dev",
    },
}


def read_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def read_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML object: {path}")
    return payload


def read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError("SKILL.md frontmatter is not closed")
    payload = yaml.safe_load(parts[1]) or {}
    if not isinstance(payload, dict):
        raise ValueError("SKILL.md frontmatter must be an object")
    return payload


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"Expected JSON object at {path}:{line_number}")
        rows.append(payload)
    return rows


def add_error(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def phrase_present(text: str, phrase: str) -> bool:
    return phrase.casefold() in text.casefold()


def grade_output(output: str, assertions: list[dict]) -> int:
    passed = 0
    for assertion in assertions:
        required = [str(item) for item in assertion.get("required", [])]
        forbidden = [str(item) for item in assertion.get("forbidden", [])]
        if all(phrase_present(output, item) for item in required) and not any(
            phrase_present(output, item) for item in forbidden
        ):
            passed += 1
    return passed


def estimate_initial_tokens() -> int:
    paths = [ROOT / "SKILL.md", ROOT / "agents" / "interface.yaml", ROOT / "agents" / "openai.yaml"]
    return sum(max(1, len(path.read_text(encoding="utf-8")) // 4) for path in paths)


def validate_source() -> dict:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        add_error(errors, (ROOT / relative).is_file(), f"Missing required file: {relative}")
    for report_name in REQUIRED_GATE_REPORTS:
        add_error(errors, (ROOT / "reports" / report_name).is_file(), f"Missing gate report: reports/{report_name}")
    if errors:
        return {"ok": False, "errors": errors, "stats": {}}

    try:
        frontmatter = read_frontmatter(ROOT / "SKILL.md")
        manifest = read_json(ROOT / "manifest.json")
        interface_doc = read_yaml(ROOT / "agents" / "interface.yaml")
        openai_doc = read_yaml(ROOT / "agents" / "openai.yaml")
        skill_ir = read_json(ROOT / "skill-ir" / "examples" / "simple-dev.json")
        semantic = read_json(ROOT / "evals" / "semantic_config.json")
        triggers = read_json(ROOT / "evals" / "trigger_cases.json")
        expectations = read_json(ROOT / "evals" / "packaging_expectations.json")
        output_cases = read_jsonl(ROOT / "evals" / "output" / "cases.jsonl")
        gate_reports = {name: read_json(ROOT / "reports" / name) for name in REQUIRED_GATE_REPORTS}
        native_smoke = read_json(ROOT / "reports" / "native_smoke.json")
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        return {"ok": False, "errors": [str(exc)], "stats": {}}

    description = str(frontmatter.get("description", ""))
    metadata = frontmatter.get("metadata", {})
    add_error(errors, frontmatter.get("name") == "simple-dev", "Frontmatter name must be simple-dev")
    add_error(errors, bool(description), "Frontmatter description is required")
    add_error(errors, len(description) <= 1024, "Frontmatter description exceeds 1024 characters")
    add_error(errors, frontmatter.get("license") == "Apache-2.0", "Frontmatter license must be Apache-2.0")
    add_error(errors, isinstance(metadata, dict), "Frontmatter metadata must be an object")
    if isinstance(metadata, dict):
        add_error(errors, metadata.get("author") == "simple-dev maintainers", "Frontmatter author mismatch")
        add_error(errors, metadata.get("version") == "1.0.0", "Frontmatter version mismatch")
    add_error(errors, "no runtime dependencies" in str(frontmatter.get("compatibility", "")), "Compatibility must state no runtime dependencies")

    required_manifest = {
        "name": "simple-dev",
        "version": "1.0.0",
        "owner": "simple-dev maintainers",
        "license": "Apache-2.0",
        "status": "experimental",
        "release_channel": "beta",
        "maturity_tier": "library",
        "lifecycle_stage": "library",
        "context_budget_tier": "scaffold",
        "review_cadence": "quarterly",
        "review_due": "2026-09-20",
    }
    for field, expected in required_manifest.items():
        add_error(errors, manifest.get(field) == expected, f"manifest.{field} must be {expected!r}")
    add_error(errors, manifest.get("target_platforms") == DECLARED_TARGETS, "Manifest target platform order or values mismatch")

    interface = interface_doc.get("interface", {})
    compatibility = interface_doc.get("compatibility", {})
    degradation = compatibility.get("degradation", {})
    add_error(errors, interface == openai_doc.get("interface", {}), "OpenAI and canonical interface metadata differ")
    add_error(errors, compatibility.get("canonical_format") == "agent-skills", "Canonical format must be agent-skills")
    add_error(errors, compatibility.get("adapter_targets") == TARGETS, "Canonical adapter targets mismatch")
    add_error(errors, set(degradation) == set(TARGETS), "Every target needs exactly one degradation entry")
    add_error(errors, compatibility.get("activation", {}).get("mode") == "implicit", "Activation must remain implicit")
    add_error(errors, compatibility.get("trust", {}).get("remote_inline_execution") == "forbid", "Remote inline execution must be forbidden")

    trigger_surface = skill_ir.get("trigger_surface", {})
    add_error(errors, skill_ir.get("schema_version") == "2.0.0", "Skill IR schema must be 2.0.0")
    add_error(errors, skill_ir.get("name") == "simple-dev", "Skill IR name mismatch")
    add_error(errors, trigger_surface.get("description") == description, "Skill IR description drifted from SKILL.md")
    add_error(errors, skill_ir.get("targets") == DECLARED_TARGETS, "Skill IR targets mismatch")
    add_error(errors, skill_ir.get("governance", {}).get("owner") == manifest.get("owner"), "Skill IR owner mismatch")
    for relative in skill_ir.get("source_files", []):
        add_error(errors, not Path(relative).is_absolute() and ".." not in Path(relative).parts, f"Unsafe Skill IR source path: {relative}")
        add_error(errors, (ROOT / relative).exists(), f"Missing Skill IR source: {relative}")

    should = triggers.get("should_trigger", [])
    should_not = triggers.get("should_not_trigger", [])
    neighbors = triggers.get("near_neighbor", [])
    add_error(errors, len(should) >= 12, "Trigger suite needs at least 12 positive cases")
    add_error(errors, len(should_not) >= 4, "Trigger suite needs at least 4 negative cases")
    add_error(errors, len(neighbors) >= 4, "Trigger suite needs at least 4 near-neighbor cases")
    families = {str(item.get("family")) for item in should if isinstance(item, dict)}
    add_error(errors, {"openai_explicit", "claude_explicit", "vscode_explicit", "generic_explicit"} <= families, "Missing explicit platform trigger cases")
    positive_phrases = [
        str(phrase)
        for concept in semantic.get("positive_concepts", {}).values()
        for phrase in concept.get("phrases", [])
    ]
    for item in should:
        text = str(item.get("text", ""))
        add_error(errors, any(phrase_present(text, phrase) for phrase in positive_phrases), f"Positive trigger has no explicit simple-dev signal: {text}")
    for bucket_name, bucket in (("should_not_trigger", should_not), ("near_neighbor", neighbors)):
        for item in bucket:
            text = str(item.get("text", ""))
            add_error(errors, not any(phrase_present(text, phrase) for phrase in positive_phrases), f"{bucket_name} accidentally includes a simple-dev signal: {text}")

    add_error(errors, len(output_cases) >= 5, "Output eval needs at least 5 cases")
    baseline_passed = 0
    skill_passed = 0
    total_assertions = 0
    for case in output_cases:
        assertions = case.get("assertions", [])
        add_error(errors, case.get("execution", {}).get("mode") == "recorded_fixture", f"Output case must be labeled recorded_fixture: {case.get('id')}")
        baseline_score = grade_output(str(case.get("baseline_output", "")), assertions)
        skill_score = grade_output(str(case.get("with_skill_output", "")), assertions)
        total_assertions += len(assertions)
        baseline_passed += baseline_score
        skill_passed += skill_score
        add_error(errors, skill_score == len(assertions), f"with_skill output failed assertions: {case.get('id')}")
        add_error(errors, skill_score > baseline_score, f"Output case shows no improvement: {case.get('id')}")

    for report_name, report in gate_reports.items():
        add_error(errors, report.get("ok") is True, f"Gate report is not passing: reports/{report_name}")
    native_targets = native_smoke.get("targets", {})
    add_error(errors, native_smoke.get("release_status") == "beta", "Native smoke evidence must preserve beta status")
    add_error(errors, native_targets.get("generic", {}).get("status") == "spec-validated", "Generic target must remain spec-validated")
    for target in ("openai", "claude", "vscode"):
        add_error(
            errors,
            native_targets.get(target, {}).get("status") == "missing evidence",
            f"{target} native status must remain missing evidence until a client smoke test passes",
        )

    add_error(errors, expectations.get("required_targets") == TARGETS, "Packaging expectations targets mismatch")
    initial_tokens = estimate_initial_tokens()
    add_error(errors, initial_tokens <= 700, f"Initial context exceeds scaffold budget: {initial_tokens} > 700")
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    add_error(errors, "Apache License" in license_text and "Version 2.0" in license_text, "LICENSE is not Apache-2.0 text")

    return {
        "ok": not errors,
        "errors": errors,
        "stats": {
            "description_characters": len(description),
            "estimated_initial_tokens": initial_tokens,
            "trigger_cases": {
                "should_trigger": len(should),
                "should_not_trigger": len(should_not),
                "near_neighbor": len(neighbors),
            },
            "output_cases": len(output_cases),
            "baseline_assertion_pass_rate": round(baseline_passed / max(total_assertions, 1), 4),
            "with_skill_assertion_pass_rate": round(skill_passed / max(total_assertions, 1), 4),
            "targets": TARGETS,
        },
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_entry(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def copy_evidence_reports(source: Path, destination: Path) -> None:
    """Copy review evidence without raw telemetry or nested build artifacts."""
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part in EVIDENCE_EXCLUDES for part in relative.parts):
            continue
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def write_deterministic_zip(source: Path, output: Path) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in source.rglob("*") if item.is_file()):
            relative = PurePosixPath(*path.relative_to(source).parts)
            info = zipfile.ZipInfo(str(relative), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def adapter_payload(target: str, manifest: dict, interface_doc: dict, native_evidence: dict) -> dict:
    compatibility = interface_doc["compatibility"]
    target_evidence = native_evidence.get(target, {})
    default_status = "spec-validated" if target == "generic" else "missing evidence"
    return {
        "schema_version": "1.0",
        "name": manifest["name"],
        "version": manifest["version"],
        "target": target,
        "canonical_format": compatibility["canonical_format"],
        "canonical_source": "SKILL.md",
        "install": INSTALL_CONTRACTS[target],
        "activation_mode": compatibility["activation"]["mode"],
        "execution_context": compatibility["execution"]["context"],
        "trust_level": compatibility["trust"]["source_tier"],
        "remote_inline_execution": compatibility["trust"]["remote_inline_execution"],
        "degradation_strategy": compatibility["degradation"][target],
        "native_evidence": {
            "status": target_evidence.get("status", default_status),
            "detail": target_evidence.get("detail", "No native client smoke evidence is available for this target."),
        },
    }


def target_readme(target: str, adapter: dict) -> str:
    install = adapter["install"]
    return "\n".join(
        [
            f"# {target.title()} installation",
            "",
            "Install the complete `simple-dev/` directory; do not copy only `SKILL.md`.",
            "",
            f"- User paths: {', '.join(install['user_paths']) or 'client-defined'}",
            f"- Project paths: {', '.join(install['project_paths']) or 'client-defined'}",
            f"- Explicit invocation: `{install['invocation']}`",
            f"- Degradation: `{adapter['degradation_strategy']}`",
            f"- Native evidence: `{adapter['native_evidence']['status']}`",
            "",
            adapter["native_evidence"]["detail"],
            "",
        ]
    )


def build_release() -> dict:
    check = validate_source()
    if not check["ok"]:
        return check
    manifest = read_json(ROOT / "manifest.json")
    interface_doc = read_yaml(ROOT / "agents" / "interface.yaml")
    native_path = ROOT / "reports" / "native_smoke.json"
    native_evidence = read_json(native_path).get("targets", {}) if native_path.exists() else {}
    version = manifest["version"]

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="simple-dev-release-") as temp_dir:
        temp = Path(temp_dir)
        runtime_root = temp / "simple-dev"
        runtime_root.mkdir()
        for relative in RUNTIME_ENTRIES:
            copy_entry(ROOT / relative, runtime_root / relative)
        runtime_zip = DIST / f"simple-dev-{version}.zip"
        write_deterministic_zip(runtime_root.parent, runtime_zip)

        compatibility_root = temp / f"simple-dev-{version}-compatibility"
        compatibility_root.mkdir()
        matrix = {"schema_version": "1.0", "name": manifest["name"], "version": version, "targets": []}
        for target in TARGETS:
            target_dir = compatibility_root / "targets" / target
            target_dir.mkdir(parents=True)
            adapter = adapter_payload(target, manifest, interface_doc, native_evidence)
            (target_dir / "adapter.json").write_text(json.dumps(adapter, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (target_dir / "README.md").write_text(target_readme(target, adapter), encoding="utf-8")
            if target == "openai":
                copy_entry(ROOT / "agents" / "openai.yaml", target_dir / "agents" / "openai.yaml")
            matrix["targets"].append(
                {
                    "target": target,
                    "degradation_strategy": adapter["degradation_strategy"],
                    "native_evidence": adapter["native_evidence"],
                }
            )
        (compatibility_root / "compatibility-matrix.json").write_text(
            json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        lines = ["# Compatibility Matrix", "", "| Target | Degradation | Native evidence |", "| --- | --- | --- |"]
        for item in matrix["targets"]:
            lines.append(
                f"| `{item['target']}` | `{item['degradation_strategy']}` | `{item['native_evidence']['status']}` |"
            )
        (compatibility_root / "compatibility-matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        copy_entry(ROOT / "manifest.json", compatibility_root / "manifest.json")
        copy_entry(ROOT / "skill-ir" / "examples" / "simple-dev.json", compatibility_root / "skill-ir.json")
        if (ROOT / "reports").exists():
            copy_evidence_reports(ROOT / "reports", compatibility_root / "evidence")
        (compatibility_root / "release-check.json").write_text(
            json.dumps(check, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        compatibility_zip = DIST / f"simple-dev-{version}-compatibility.zip"
        write_deterministic_zip(compatibility_root.parent, compatibility_zip)

    assets = [runtime_zip, compatibility_zip]
    checksums = "\n".join(f"{sha256(path)}  {path.name}" for path in assets) + "\n"
    (DIST / "SHA256SUMS").write_text(checksums, encoding="utf-8")
    return {
        "ok": True,
        "errors": [],
        "artifacts": [str(path.relative_to(ROOT)) for path in [*assets, DIST / "SHA256SUMS"]],
        "checksums": {path.name: sha256(path) for path in assets},
    }


def safe_zip_members(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    for name in names:
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError(f"Unsafe archive member in {path.name}: {name}")
    return names


def verify_release() -> dict:
    errors: list[str] = []
    manifest = read_json(ROOT / "manifest.json")
    version = manifest["version"]
    runtime_zip = DIST / f"simple-dev-{version}.zip"
    compatibility_zip = DIST / f"simple-dev-{version}-compatibility.zip"
    checksum_path = DIST / "SHA256SUMS"
    for path in (runtime_zip, compatibility_zip, checksum_path):
        add_error(errors, path.is_file(), f"Missing release artifact: {path.relative_to(ROOT)}")
    if errors:
        return {"ok": False, "errors": errors}

    expected = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        expected[name] = digest
    for path in (runtime_zip, compatibility_zip):
        add_error(errors, expected.get(path.name) == sha256(path), f"Checksum mismatch: {path.name}")

    try:
        runtime_names = safe_zip_members(runtime_zip)
        compatibility_names = safe_zip_members(compatibility_zip)
    except ValueError as exc:
        errors.append(str(exc))
        runtime_names = []
        compatibility_names = []

    required_runtime = {f"simple-dev/{relative}" for relative in ["SKILL.md", "README.md", "LICENSE", "manifest.json", "agents/interface.yaml"]}
    add_error(errors, required_runtime <= set(runtime_names), "Runtime ZIP is missing required files")
    add_error(errors, not any("/tools/" in name or "/.github/" in name or "/dist/" in name for name in runtime_names), "Runtime ZIP contains build-only files")
    compat_root = f"simple-dev-{version}-compatibility"
    required_compat = {
        f"{compat_root}/compatibility-matrix.json",
        *{f"{compat_root}/targets/{target}/adapter.json" for target in TARGETS},
    }
    add_error(errors, required_compat <= set(compatibility_names), "Compatibility ZIP is missing target adapters")

    install_results = {}
    with tempfile.TemporaryDirectory(prefix="simple-dev-install-") as temp_dir:
        temp = Path(temp_dir)
        if runtime_names:
            with zipfile.ZipFile(runtime_zip) as archive:
                archive.extractall(temp / "extracted")
            source = temp / "extracted" / "simple-dev"
            for target in TARGETS:
                destination = temp / "installs" / target / "simple-dev"
                shutil.copytree(source, destination)
                ok = (destination / "SKILL.md").is_file() and read_frontmatter(destination / "SKILL.md").get("name") == "simple-dev"
                install_results[target] = ok
                add_error(errors, ok, f"Install simulation failed: {target}")

    return {
        "ok": not errors,
        "errors": errors,
        "checksums": expected,
        "install_simulation": install_results,
    }


def main() -> None:
    if sys.version_info < (3, 12):
        raise SystemExit("Python 3.12+ is required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "build", "verify"])
    args = parser.parse_args()
    if args.command == "check":
        report = validate_source()
    elif args.command == "build":
        report = build_release()
    else:
        report = verify_release()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report.get("ok") else 2)


if __name__ == "__main__":
    main()
