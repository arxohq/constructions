#!/usr/bin/env python3
"""Verify the immutable edition and rerun its selected examples in a fresh copy.

Copyright 2026 Rifat Jumagulov. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(command, *, cwd):
    result = subprocess.run(
        list(map(str, command)), cwd=cwd, capture_output=True, text=True,
        timeout=120, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    require(result.returncode == 0,
            f"Command failed: {command}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def integrity():
    companion = ROOT / "companion"
    provenance = read_json(ROOT / "provenance.json")
    require(digest(companion / "bundle-manifest.json") ==
            provenance["companion_manifest_sha256"], "Edition manifest changed")
    manifest = read_json(companion / "bundle-manifest.json")
    expected = manifest["files"]
    actual = set()
    for path in companion.rglob("*"):
        require(not path.is_symlink(), f"Unexpected symlink: {path}")
        if path.is_file():
            actual.add(path.relative_to(companion).as_posix())
    require(actual == set(expected) | {"bundle-manifest.json"},
            f"Edition files differ: {actual ^ (set(expected) | {'bundle-manifest.json'})}")
    for name, sha256 in expected.items():
        require(digest(companion / name) == sha256, f"Changed edition file: {name}")
    print(f"Integrity: {len(expected)} edition files match", flush=True)
    return {"status": "passed", "edition_files": len(expected),
            "manifest_sha256": provenance["companion_manifest_sha256"]}


def runtime():
    law = shutil.which("law")
    require(law, "Run npm ci, then npm test (the pinned CLI must be on PATH)")
    version = json.loads(run([law, "version", "--json"], cwd=ROOT))
    edition = read_json(ROOT / "companion/execution.json")
    require(version["tool"] == edition["binary"]["tool"], "Unexpected CLI version")
    require(version["semantics"] == edition["binary"]["semantics"], "Unexpected semantics")
    results = []
    with tempfile.TemporaryDirectory(prefix="constructions-ci-") as temporary:
        work = Path(temporary)
        companion = work / "companion"
        shutil.copytree(ROOT / "companion", companion)
        reader = companion / "reader"
        for test in edition["tests"]:
            package = test["package"]
            command = [law, "engine", "test", reader / test["test"],
                       "--program", reader / "corpus/clir" / f"{package}.lawir.json",
                       "--imports", reader / "contexts" / f"{package}.json", "--json"]
            result = json.loads(run(command, cwd=reader))
            require(result.get("ok") is True and result.get("failed") == 0, str(result))
            require(result["total"] == test["total"] and result["passed"] == test["passed"],
                    f"Scenario count changed: {test['test']}")
            results.append({"test": test["test"], "package": package,
                            "passed": result["passed"], "total": result["total"]})
        passed = sum(item["passed"] for item in results)
        require(passed == edition["passed"] == 383, "Expected 383 selected scenarios")
        print(f"Selected examples: {passed} scenarios in {len(results)} files passed", flush=True)
        water = json.loads(run(["python3", "-B", companion / "check_reader.py",
                                "--law", law, "--bundle", companion,
                                "--out", work / "water"], cwd=reader))
        run(["python3", "-B", reader / "packs/demo/expense-evidence/run_demo.py"], cwd=reader)
        print("Water replay, four support states and expense evidence: passed", flush=True)
    return {"status": "passed", "platform": platform.platform(), "cli": version,
            "test_files": len(results), "scenarios": passed, "tests": results,
            "water": water, "expense_evidence": "passed",
            "printed_50_blocks": "historical acceptance retained; not rerun by this check"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "ci-results/summary.json")
    args = parser.parse_args()
    report = {"integrity": integrity()}
    if args.runtime:
        report["runtime"] = runtime()
        integrity()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
