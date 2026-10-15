#!/usr/bin/env python3
"""Байтовый differential демонстрации: lawref против lawc на каждой сцене.

Контракт §78.2 — байтовое совпадение канонического evaluation-документа §208,
а не совпадение кода: реализации написаны независимо (DECISION-0126 §3).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK = HERE.parent
ROOT = PACK.parents[2]
sys.path.insert(0, str(ROOT / "engines" / "lawref"))

IR = PACK / "clir" / "expense-evidence.lawir.json"
LAWTEST = PACK / "tests" / "reimbursement.lawtest"


def lower_tests() -> list[dict]:
    out = subprocess.run(
        ["cargo", "run", "-q", "--manifest-path", str(ROOT / "engines/lawc/Cargo.toml"),
         "-p", "law-cli", "--", "lower-test", str(LAWTEST), "--all"],
        capture_output=True, check=True)
    return json.loads(out.stdout)["document"]["tests"]


def lawc_eval(request: dict, workdir: Path) -> bytes:
    """`lawc eval <каталог>` читает `request.json` — тот же закрытый вход."""
    (workdir / "request.json").write_text(
        json.dumps(request, ensure_ascii=False), encoding="utf-8")
    out = subprocess.run(
        ["cargo", "run", "-q", "--manifest-path", str(ROOT / "engines/lawc/Cargo.toml"),
         "-p", "law-cli", "--", "eval", str(workdir),
         "--semantic-version", request["semanticVersion"]],
        capture_output=True, check=True)
    return out.stdout


def main() -> int:
    import tempfile

    from lawref.canon import canonical_bytes
    from lawref.evaluator.engine import EvaluationRequest, evaluate

    ir = json.loads(IR.read_text(encoding="utf-8"))
    failures = 0
    for test in lower_tests():
        case, query = test["case"], test["query"]
        wire = {
            "schemaVersion": "law.core.evaluation-request/0.2",
            "semanticVersion": "0.2",
            "ir": ir, "case": case, "query": query,
        }
        oracle = canonical_bytes(evaluate(EvaluationRequest.from_dict(wire)))
        with tempfile.TemporaryDirectory() as workdir:
            engine = lawc_eval(wire, Path(workdir))
        title = test.get("title", "?")
        if oracle == engine:
            print(f"  OK  {title}")
        else:
            failures += 1
            print(f"FAIL  {title}")
            left = json.loads(oracle)
            right = json.loads(engine)
            for key in sorted(set(left) | set(right)):
                if left.get(key) != right.get(key):
                    print(f"      расходится: {key}")
    print(f"differential демонстрации: {'PASS' if not failures else 'FAIL'} "
          f"({failures} расхождений)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
