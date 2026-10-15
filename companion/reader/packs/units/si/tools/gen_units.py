#!/usr/bin/env python3
"""Генератор пакета единиц SI: `units.json` → `si.law` и узлы CLIR (§49.2).

Источник истины — `units.json`; `.law` ПОРОЖДАЕТСЯ и руками не правится
(инвариант 2 CLAUDE.md). `--check` не пишет ничего и краснеет при расхождении:
им пользуются ворота.

Здесь нет ни строчки семантики (инвариант 5): генератор перекладывает
объявления в поверхность и в узлы, а разрешение имён, размерность и масштаб
считают реализации по §49.2.

    python3 packs/units/si/tools/gen_units.py
    python3 packs/units/si/tools/gen_units.py --check
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PACK = Path(__file__).resolve().parents[1]
DATA = PACK / "units.json"
SOURCE = PACK / "si.law"

#: Вход ПАКЕТА (рамка 3 DECISION-0068 в редакции E-0068): флаг стоит и в
#: манифесте `[features]`, и у каждого объявления — `check_features` сверяет
#: его с реестром `spec/feature-registry.json`, и отзыв флага обязан покрасить
#: пакет, а не молча оставить единицы объявленными.
FLAG = '@requires_feature("law.units/0.1")\n'

HEADER = """// ПОРОЖДЁННЫЙ ФАЙЛ. Источник истины — units.json; правки вносятся туда и
// раскатываются `python3 packs/units/si/tools/gen_units.py` (инвариант 2).
//
// Пакет единиц SI (DECISION-0154, §49.2). Это НЕ словарь `vocab.*` и не
// ресурс §85: объявления единиц — программные узлы, приходящие потребителю
// закреплённой зависимостью, и алгебра §49.1 разрешает по ним теги величин.

language "law.core" version "0.2";
package units.si version "0.1.0";
namespace "urn:law:units:si";

"""


def _repeat(items: list) -> str:
    """Степень записывается ПОВТОРЕНИЕМ (`m * m`), а не оператором `^`.

    У лексера §13 лексемы `^` нет, и заводить её ради одной декларации значило
    бы впустить новый символ во все выражения; повторы складывает сам парсер.
    """
    return " * ".join(name for name, exp in items for _ in range(exp))


def dimension_text(pairs: list) -> str:
    """`[["Length", 3]]` → `Length * Length * Length`."""
    num = [(b, e) for b, e in pairs if e > 0]
    den = [(b, -e) for b, e in pairs if e < 0]
    head = _repeat(num) if num else "1"
    return f"{head} / ({_repeat(den)})" if den else head


def factor_text(factors: list) -> str:
    """`[["m", 1], ["s", -1]]` → `m / s`."""
    num = [(u, e) for u, e in factors if e > 0]
    den = [(u, -e) for u, e in factors if e < 0]
    head = _repeat(num) if num else "1"
    return f"{head} / {_repeat(den)}" if den else head


def render(data: dict) -> str:
    out = [
        HEADER,
        "// --- Простые единицы: атом с точным масштабом и размерностью ---\n\n",
    ]
    for unit in data["simple"]:
        out.append(FLAG)
        out.append(
            f'pub unit {unit["name"]} dimension {dimension_text(unit["dimension"])} '
            f'scale {unit["scaleNum"]} / {unit["scaleDen"]};\n'
        )
        for alias in unit["aliases"]:
            out.append(FLAG)
            out.append(f'pub unit alias {alias} = {unit["name"]};\n')
    out.append("\n// --- Производные единицы: произведение и частное простых ---\n\n")
    for unit in data["derived"]:
        out.append(FLAG)
        out.append(
            f'pub derived unit {unit["name"]} = {factor_text(unit["factors"])};\n'
        )
        for alias in unit["aliases"]:
            out.append(FLAG)
            out.append(f'pub unit alias {alias} = {unit["name"]};\n')
    if data.get("atomic"):
        out.append("\n// --- Масштабированные атомы (§49.2, DECISION-0157) ---\n\n")
    for unit in data.get("atomic", []):
        out.append(f'// {unit["definition"]}\n// {unit["source"]}\n')
        out.append(FLAG)
        out.append(f'pub unit {unit["name"]} = {unit["expression"]};\n')
        for alias in unit.get("aliases", []):
            out.append(FLAG)
            out.append(f'pub unit alias {alias} = {unit["name"]};\n')
    return "".join(out)


def _node(namespace: str, body: dict) -> dict:
    """Узел `unit_decl` с общими полями §201 (`package`, `contentHash`).

    Хэш считает сам оракул (`lawref.authoring.content_hash`): вторая формула
    разошлась бы с первой молча, и узлы генератора не совпали бы с узлами
    компилятора по байтам.
    """
    import sys

    sys.path.insert(0, str(ROOT / "engines" / "lawref"))
    from lawref.authoring import content_hash

    node = {"package": namespace, **body}
    node["contentHash"] = content_hash(node)
    return node


def nodes(data: dict) -> list[dict]:
    """Узлы `unit_decl` (§49.2) — тот же состав, что понижает компилятор.

    Нужны потребителям, у которых CLIR рукописный: conformance-векторы до M3
    и пробы. Порядок — объявления, как в `units.json`; канон документа §208
    сортирует узлы сам.
    """
    namespace = data["namespace"]
    out: list[dict] = []
    for unit in data["simple"]:
        out.append(
            _node(
                namespace,
                {
                    "kind": "unit_decl",
                    "id": f'{namespace}#{unit["name"]}',
                    "unitName": unit["name"],
                    "unitKind": "simple",
                    "public": True,
                    "dimension": [[base, exp] for base, exp in unit["dimension"]],
                    "scaleNum": unit["scaleNum"],
                    "scaleDen": unit["scaleDen"],
                },
            )
        )
        out.extend(_alias(namespace, alias, unit["name"]) for alias in unit["aliases"])
    for unit in data["derived"]:
        out.append(
            _node(
                namespace,
                {
                    "kind": "unit_decl",
                    "id": f'{namespace}#{unit["name"]}',
                    "unitName": unit["name"],
                    "unitKind": "derived",
                    "public": True,
                    "factors": [{"unit": u, "exp": e} for u, e in unit["factors"]],
                },
            )
        )
        out.extend(_alias(namespace, alias, unit["name"]) for alias in unit["aliases"])
    from lawref.unit_declarations import normalize

    atomic = []
    for unit in data.get("atomic", []):
        atomic.append(
            {
                "kind": "unit_decl",
                "id": f'{namespace}#{unit["name"]}',
                "package": namespace,
                "unitName": unit["name"],
                "public": True,
                "expression": unit["expression"],
            }
        )
    out.extend(_node(namespace, n) for n in normalize(atomic, out))
    for unit in data.get("atomic", []):
        out.extend(_alias(namespace, a, unit["name"]) for a in unit.get("aliases", []))
    return [_node(namespace, node) for node in normalize(out)]


def _alias(namespace: str, alias: str, target: str) -> dict:
    return _node(
        namespace,
        {
            "kind": "unit_decl",
            "id": f"{namespace}#{alias}",
            "unitName": alias,
            "unitKind": "alias",
            "public": True,
            "target": target,
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="ничего не писать; краснеть при расхождении si.law с units.json",
    )
    args = parser.parse_args()
    data = json.loads(DATA.read_text(encoding="utf-8"))
    text = render(data)
    if args.check:
        current = SOURCE.read_text(encoding="utf-8") if SOURCE.exists() else ""
        if current != text:
            print(
                f"gen_units: FAIL {SOURCE.relative_to(ROOT)} разошёлся с units.json "
                "— перегенерируйте (инвариант 2)",
                file=sys.stderr,
            )
            return 1
        print(
            f"gen_units: OK {len(data['simple']) + len(data.get('atomic', []))} простых, {len(data['derived'])} производных"
        )
        return 0
    SOURCE.write_text(text, encoding="utf-8")
    print(
        f"gen_units: записан {SOURCE.relative_to(ROOT)} "
        f"({len(data['simple']) + len(data.get('atomic', []))} простых, {len(data['derived'])} производных, "
        f"{len(nodes(data))} узлов unit_decl)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
