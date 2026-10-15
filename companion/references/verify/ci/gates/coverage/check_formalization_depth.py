#!/usr/bin/env python3
"""Глубина формализации по статьям — храповик против тихого регресса.

Мера §33.1 (EXECUTABLE / ANCHORED / SOURCE_ONLY) до этих ворот жила только в
скилле `formalize-act` и в воротах не участвовала. Следствие: снятие правила,
переезд якоря или замена нормы описательным фактом уменьшали глубину, и не
падало ничего — `verify/ci/gates/sources/check_source_pinning.py` считает статью «с фрагментом» и
такой сдвиг не видит по построению.

Реализация меры НЕ дублируется: модуль импортируется из скилла по пути. Вторая
копия соглашения — ровно тот дефект, который чинился в `article_text` (там
`ARTICLE_RE` и срез разошлись по точке после номера статьи, и проверка причин
объявленных границ работала вхолостую на всей Конституции).

Храповик односторонний: рост глубины разрешён и печатается, падение — отказ.
Порог именно такой, потому что двусторонний гейт был бы красным при каждой
правке корпуса и его научились бы игнорировать (довод `verify/ci/gates/release/build_release.py`).

    python3 verify/ci/gates/coverage/check_formalization_depth.py                      # проверка
    python3 verify/ci/gates/coverage/check_formalization_depth.py --canary             # мутации
    python3 verify/ci/gates/coverage/check_formalization_depth.py --only <акт>         # сверить один
    python3 verify/ci/gates/coverage/check_formalization_depth.py --register <акт>     # вписать один
    python3 verify/ci/gates/coverage/check_formalization_depth.py --rename <был> <стал>  # переезд
    python3 verify/ci/gates/coverage/check_formalization_depth.py --write              # ВСЮ базу
"""
from __future__ import annotations

import importlib.util
import hashlib
import json
import re
import sys
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 used by the repository CI launcher.
    import tomli as tomllib

# Ворота живут в `verify/ci/gates/<класс>/`, поэтому до корня репозитория
# три шага, а не один.
ROOT = Path(__file__).resolve().parents[4]
MEASURE = ROOT / ".claude/skills/formalize-act/scripts/boundaries.py"
BASELINE = ROOT / "verify/ci/data/formalization-depth.json"

#: Уровни, по которым идёт храповик, и направление допустимого движения.
#: `UNEXPLAINED` — статьи уровня SOURCE_ONLY, о которых пакет не сказал ничего:
#: ни нормы, ни объявленной границы с причиной. Это единственная величина,
#: которую можно двигать вниз двумя разными способами — формализовать статью
#: или честно объявить её границей, — и оба считаются прогрессом.
#: `EXCLUDED` — как и `ANCHORED`, направление 0: список `excluded` в
#: `articles.json` заводится руками и не поверяется ничем независимым (в
#: отличие от EXECUTABLE, за которым стоит differential). Любое его движение —
#: и рост (неотличим от тихого бегства из-под SOURCE_ONLY/UNEXPLAINED
#: объявлением вместо формализации), и падение (пропавшая при правке JSON
#: запись, без проверки, что статья и правда снова в измеряемой редакции) —
#: требует осознанного `--write`, а не автоматического зачёта.
#: `INTERPRETED` — статья, из которой выводится ТОЛЬКО при выбранном прочтении
#: §152: правило написано и исполнимо, но `include` вывел его из базовой
#: теории, и на обычном деле его нет. Направление 0, как у `ANCHORED` и
#: `EXCLUDED`, и по той же причине: рост неотличим от тихого бегства из-под
#: `EXECUTABLE` (пометил `include`-ом — и статья перестала обещать вывод), а
#: падение — от снятия чужого прочтения без проверки, что оно и правда лишнее.
#: Уровень заведён 29.08.2026: до него гейт толкования был для меры невидим, и
#: четыре статьи Регламента (ЕС) 261/2004 стояли `EXECUTABLE`, пока их
#: обязанностей не существовало ни на одном деле.
RATCHET = {"EXECUTABLE": +1, "ANCHORED": 0, "INTERPRETED": 0,
           "SOURCE_ONLY": -1, "UNEXPLAINED": -1, "EXCLUDED": 0}


_PINNING = None


def pinning():
    """Разбор `declared` берётся из ворот закрепления, а не переписывается."""
    global _PINNING
    if _PINNING is None:
        spec = importlib.util.spec_from_file_location(
            "check_source_pinning", ROOT / "verify/ci/gates/sources/check_source_pinning.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _PINNING = module
    return _PINNING


def load_measure():
    spec = importlib.util.spec_from_file_location("boundaries", MEASURE)
    if spec is None or spec.loader is None:
        sys.exit(f"мера не найдена: {MEASURE.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: Почему мера пропускает акт. Строки — ЧАСТЬ ответа, а не комментарий: их
#: печатает `corpus/tools/checks/doctor.py`, отвечая на вопрос «вписывать ли акт в
#: базу». Пока причина жила комментарием внутри цикла, doctor отвечал на тот
#: же вопрос своим счётом («ключа нет — пробел») и советовал вписать раздел
#: акту, которого мера не отдаёт НИКОГДА, — а любая такая запись делает эти
#: ворота красными навсегда: `main()` объявляет регрессом всё, что есть в базе
#: и чего нет в измерении (замерено на `"hippocratic-oath": null` — ровно
#: такая запись стояла в базе до перезаморозки 29.08.2026).
NO_SOURCE = ("мера не видит закреплённых байтов "
             "(фаза 0 не выполнена либо имя документа вне соглашения меры)")
NO_CLIR = "CLIR не разрешается по namespace исходников — акт не лоуверен"
NO_LAWS = "собственных .law у пакета нет"
NO_UNIT = "глубина по единицам неприменима (единицы деления у акта нет)"
NOT_APPLICABLE_PREFIX = "NOT_APPLICABLE: "
INVALID_MARKER_PREFIX = "invalid formalizationDepth metadata: "
# Until an independent, centrally reviewed registry exists, this exception is
# deliberately closed-world. Package authors cannot opt legal acts out of
# §33.1 merely by self-attesting `instrument=engineering_methodology`.
NOT_APPLICABLE_METHODOLOGIES = {
    "mining-bvr-parameters": "TRUBETSKOY_1994",
    "gornoe-byuro-equipment-productivity": "VNTP_13_1_86",
}


def composite_depth_path(boundaries, act: str) -> Path | None:
    """Optional, package-local composite axis. Conventional acts never use it.

    Presence of this versioned sidecar is the opt-in. Keeping it out of
    package-manifest metadata avoids changing the global manifest contract.
    """
    package = boundaries.act_dir(act)
    if package is None:
        return None
    candidate = package / "sources/formalization-depth-composite.json"
    if not candidate.is_file():
        return None
    # Composite measurement changes the denominator and therefore must not be
    # self-enabled by arbitrary package metadata. Keep the initial rollout
    # closed to the one reviewed package until a central allowlist is approved.
    if act != "kz-hazardous-facility-declaration":
        raise ValueError(f"composite depth is not authorized for {act}")
    return candidate


def composite_counts(boundaries, act: str, clir_paths: list[Path], config_path: Path) -> dict[str, int]:
    """Measure an explicitly declared set of namespaced units across pinned sources.

    This opt-in path is intentionally data-driven and closed: every unit names
    its publication, edition and exact fragment locator. A broad fragment may
    represent one aggregate unit, but can never silently become row-level
    coverage because row units must identify row-specific fragments.
    """
    package = boundaries.act_dir(act)
    if package is None:
        raise ValueError(f"{act}: composite map requires a package directory")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schema") != "law.formalization-depth-composite.v1":
        raise ValueError("unsupported composite depth schema")
    sources_text = (package / "sources.law").read_text(encoding="utf-8")
    publications = {}
    block_re = re.compile(
        r"(?m)^\s*publication\s+([A-Za-z_][A-Za-z0-9_]*)\s+of\s+"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*\{(.*?)\}", re.S)
    for match in block_re.finditer(sources_text):
        symbol = match.group(1)
        local = re.search(r'\blocal_path\s+"([^"]+)"\s*;', match.group(3))
        digest = re.search(r'\bcontent_hash\s+"sha256:([0-9a-f]{64})"\s*;', match.group(3))
        if local is None or digest is None:
            raise ValueError(f"publication {symbol} lacks exact local_path/content_hash")
        if symbol in publications:
            raise ValueError(f"duplicate publication symbol in sources.law: {symbol}")
        publications[symbol] = (match.group(2), local.group(1), digest.group(1))

    nodes: dict[str, dict] = {}
    for path in clir_paths:
        for node in json.loads(path.read_text(encoding="utf-8")).get("nodes", []):
            nodes.setdefault(str(node.get("id", "")), node)
    gated = boundaries.interpretation_gated(list(nodes.values()))
    position_ids = {
        str(node.get("id", "")) for node in nodes.values()
        if boundaries.is_position_node(node)
    }
    position_templates = {item.replace("#Position", "#", 1) for item in position_ids}
    counts = {level: 0 for level in RATCHET}
    counts["—"] = 0
    seen: set[str] = set()

    for component in config.get("components", []):
        required = {"id", "namespace", "publication_symbol", "publication", "edition_symbol", "edition", "local_path", "sha256", "scope", "units", "inventory"}
        if not isinstance(component, dict) or not required <= component.keys():
            raise ValueError("composite component is missing required metadata")
        source_path = (package / component["local_path"]).resolve()
        try:
            source_path.relative_to(package.resolve())
        except ValueError as exc:
            raise ValueError("composite source path escapes package") from exc
        publication = publications.get(component["publication_symbol"])
        actual = hashlib.sha256(source_path.read_bytes()).hexdigest() if source_path.is_file() else None
        if (publication != (component["edition_symbol"], component["local_path"], component["sha256"])
                or actual != component["sha256"]):
            raise ValueError(f"{component['id']}: composite source is not the pinned publication")
        pub_node = nodes.get(component["publication"])
        if (pub_node is None or pub_node.get("kind") != "publication"
                or pub_node.get("documentHash") != f"sha256:{component['sha256']}"
                or pub_node.get("edition") != component["edition"]):
            raise ValueError(f"{component['id']}: pinned publication is absent from CLIR")
        source_text = source_path.read_text(encoding="utf-8")
        allowed_scope = set(component["scope"])
        if not allowed_scope:
            raise ValueError(f"{component['id']}: empty composite scope")
        inventory = component["inventory"]
        if inventory.get("kind") == "numbered_points":
            extraction = inventory.get("extractor", {})
            extraction_declaration = {
                "unit": "point_in_section",
                "locator": "point",
                "section_start": extraction.get("section_start"),
                "section_end": extraction.get("section_end"),
            }
            if not extraction_declaration["section_start"] or not extraction_declaration["section_end"]:
                raise ValueError(f"{component['id']}: point inventory requires exact section bounds")
            extracted = boundaries.article_matches(source_text, "point_in_section", extraction_declaration)
            extracted_inventory = [(str(match.group(1)).replace("_", "-"),
                                    " ".join(str(match.group(2) or "").split()))
                                   for match in extracted]
            # Section headings can reuse a number immediately before the
            # operative point (e.g. "1. Общие положения" then point 1). Such
            # headings are removed only by exact, component-local declarations;
            # unexplained duplicate numbered units fail closed.
            section_start = source_text.index(extraction_declaration["section_start"])
            section_end = source_text.index(extraction_declaration["section_end"], section_start)
            section_text = source_text[section_start:section_end]
            for heading in inventory.get("structural_headings", []):
                number = str(heading.get("number"))
                title = " ".join(str(heading.get("title", "")).split())
                if not title or section_text.count(f"{number}. {title}") != 1:
                    raise ValueError(f"{component['id']}: structural heading source line is absent or ambiguous")
                # article_matches exposes at most 90 title characters; prove
                # the full heading in pinned bytes first, then remove exactly
                # that parser occurrence (never by number/set membership).
                pair = (number, title[:90])
                try:
                    extracted_inventory.remove(pair)
                except ValueError as exc:
                    raise ValueError(f"{component['id']}: declared structural heading not found exactly once") from exc
            actual_complete_inventory = [number for number, _title in extracted_inventory]
            expected_complete_inventory = [str(value) for value in inventory.get("expected_extracted", [])]
            if sorted(actual_complete_inventory, key=lambda value: (int(value.split("-")[0]), value)) != sorted(
                    expected_complete_inventory, key=lambda value: (int(value.split("-")[0]), value)):
                raise ValueError(f"{component['id']}: complete bounded source inventory differs")
            actual_inventory = [number for number in actual_complete_inventory if number in allowed_scope]
            expected_inventory = [str(value) for value in inventory.get("expected", [])
                                  if str(value) in allowed_scope]
            if len(expected_inventory) != len(set(expected_inventory)):
                raise ValueError(f"{component['id']}: repeated legal point numbers require occurrence-specific unit IDs")
            if sorted(actual_inventory, key=lambda value: (int(value.split("-")[0]), value)) != sorted(
                    expected_inventory, key=lambda value: (int(value.split("-")[0]), value)):
                raise ValueError(f"{component['id']}: extracted inventory differs from declared complete scope")
            configured_scope = [str(unit.get("scope")) for unit in component["units"]
                                if str(unit.get("scope")) in allowed_scope]
            if sorted(configured_scope, key=lambda value: (int(value.split("-")[0]), value)) != sorted(
                    expected_inventory, key=lambda value: (int(value.split("-")[0]), value)):
                raise ValueError(f"{component['id']}: unit map does not cover the complete extracted scope")
        elif inventory.get("kind") == "table_bundle":
            headings = inventory.get("required_headings", [])
            normalized_source = " ".join(source_text.split())
            if not headings or any(normalized_source.count(" ".join(str(text).split())) != 1
                                   for text in headings):
                raise ValueError(f"{component['id']}: table bundle headings are absent or ambiguous")
            if (len(component["units"]) != 1
                    or component["units"][0].get("granularity") != "aggregate"):
                raise ValueError(f"{component['id']}: tables must remain one aggregate unit, not row units")
        else:
            raise ValueError(f"{component['id']}: unsupported inventory kind")
        for unit in component["units"]:
            if not isinstance(unit, dict) or not {"key", "scope", "fragment", "locator", "granularity"} <= unit.keys():
                raise ValueError(f"{component['id']}: malformed composite unit")
            if unit["scope"] not in allowed_scope:
                continue
            unit_id = f"{component['namespace']}/{unit['key']}"
            if unit_id in seen:
                raise ValueError(f"duplicate namespaced composite unit: {unit_id}")
            seen.add(unit_id)
            fragment = nodes.get(unit["fragment"])
            if (fragment is None or fragment.get("kind") != "fragment"
                    or fragment.get("edition") != component["edition"]
                    or fragment.get("locator") != unit["locator"]):
                raise ValueError(f"{unit_id}: fragment provenance/locator mismatch")
            excerpt = " ".join(" ".join((text.get("text") or "").split())
                               for text in fragment.get("texts", []))
            normalized_source = " ".join(source_text.split())
            if not excerpt or excerpt not in normalized_source:
                raise ValueError(f"{unit_id}: fragment text is not found in pinned source")
            if unit["granularity"] == "row" and fragment.get("locator") in ("preamble", "appendix/1", "appendix/2-1"):
                raise ValueError(f"{unit_id}: aggregate fragment cannot establish row-level coverage")
            anchored = False
            deriving = False
            interpreted = False
            for node in nodes.values():
                if boundaries.is_position_node(node) or (
                    node.get("kind") == "norm_template"
                    and str(node.get("id", "")) in position_templates
                ):
                    continue
                if unit["fragment"] not in {str(x) for x in node.get("anchors", []) or []}:
                    continue
                anchored = True
                if node.get("kind") in boundaries.DERIVING_KINDS:
                    if str(node.get("id", "")) in gated:
                        interpreted = True
                    else:
                        deriving = True
            if unit.get("excluded") and not deriving and not interpreted:
                level = "EXCLUDED"
            elif deriving:
                level = "EXECUTABLE"
            elif interpreted:
                level = "INTERPRETED"
            elif anchored:
                level = "ANCHORED"
            else:
                level = "SOURCE_ONLY"
            counts[level] += 1
            if level == "SOURCE_ONLY" and not unit.get("boundary_reason"):
                counts["UNEXPLAINED"] += 1
    if not seen:
        raise ValueError("composite map selected no units")
    return counts


def declared_non_applicable_reason(boundaries, act: str) -> str | None:
    """Явное исключение из ПРАВОВОЙ меры только для типа пакета из manifest.

    До признания границы проверяются байты каждой publication, перечисленной
    в manifest: эта проверка нужна пакетам с инженерными source-файлами, чьи
    имена не входят в соглашение `act_source` (ru.txt и аналоги). Маркер нельзя
    использовать для сокрытия отсутствующего/изменённого источника, CLIR или
    собственных правил; несогласованный маркер прекращает измерение ошибкой.
    """
    package = boundaries.act_dir(act)
    manifest_path = package / "law.toml" if package is not None else None
    if manifest_path is None or not manifest_path.is_file():
        return None
    metadata = tomllib.loads(manifest_path.read_text(encoding="utf-8")).get("metadata", {})
    marker = metadata.get("formalizationDepth")
    if marker is None:
        return None
    expected_primary_source = NOT_APPLICABLE_METHODOLOGIES.get(act)
    if expected_primary_source is None or metadata.get("act") != act:
        raise ValueError(
            f"{manifest_path.relative_to(ROOT)}: formalizationDepth not_applicable "
            "is not authorized for this act id")
    valid = (
        marker == "not_applicable"
        and metadata.get("jurisdiction") == "none"
        and metadata.get("instrument") == "engineering_methodology"
        and metadata.get("legalStatus") == "doctrine"
        and metadata.get("primarySource") == expected_primary_source
        and isinstance(metadata.get("formalizationDepthReason"), str)
        and bool(metadata["formalizationDepthReason"].strip())
    )
    if not valid:
        raise ValueError(
            f"{manifest_path.relative_to(ROOT)}: formalizationDepth marker "
            "requires jurisdiction=none, instrument=engineering_methodology, "
            "legalStatus=doctrine and a nonempty formalizationDepthReason")

    declared_paths = metadata.get("formalizationDepthSources")
    sources_path = package / "sources.law"
    if (not isinstance(declared_paths, list) or not declared_paths
            or not all(isinstance(path, str) and path for path in declared_paths)
            or not sources_path.is_file()):
        raise ValueError(
            f"{manifest_path.relative_to(ROOT)}: not_applicable requires a nonempty "
            "formalizationDepthSources list and sources.law")
    sources_text = sources_path.read_text(encoding="utf-8")
    publication_start = re.compile(
        r"(?m)^\s*publication\s+([A-Za-z_][A-Za-z0-9_]*)\s+of\s+"
        r"[A-Za-z_][A-Za-z0-9_]*\s*\{")
    publication_block = re.compile(
        r"publication\s+([A-Za-z_][A-Za-z0-9_]*)\s+of\s+"
        r"[A-Za-z_][A-Za-z0-9_]*\s*\{(.*?)\}", re.S)
    starts = list(publication_start.finditer(sources_text))
    blocks = list(publication_block.finditer(sources_text))
    if len(starts) != len(blocks):
        raise ValueError("sources.law contains an incomplete publication block")
    publications: dict[str, tuple[str, str]] = {}
    for block in blocks:
        local_path = re.search(r'\blocal_path\s+"([^"]+)"\s*;', block.group(2))
        digest = re.search(r'\bcontent_hash\s+"sha256:([0-9a-f]{64})"\s*;', block.group(2))
        if local_path is None or digest is None:
            missing = "local_path" if local_path is None else "sha256 content_hash"
            raise ValueError(f"publication {block.group(1)} has no {missing}")
        relative, sha256 = local_path.group(1), digest.group(1)
        previous = publications.get(relative)
        if previous is not None and previous[1] != sha256:
            raise ValueError(f"conflicting publication hashes for local_path {relative}")
        publications[relative] = (block.group(1), sha256)
    if len(set(declared_paths)) != len(declared_paths):
        raise ValueError("formalizationDepthSources contains duplicate paths")
    if set(declared_paths) != set(publications):
        raise ValueError(
            "formalizationDepthSources must enumerate every publication local_path "
            "from sources.law")
    for relative in declared_paths:
        publication = publications.get(relative)
        if publication is None:
            raise ValueError(f"{relative}: no matching pinned publication in sources.law")
        source_path = (package / relative).resolve()
        try:
            source_path.relative_to(package.resolve())
        except ValueError as exc:
            raise ValueError(f"{relative}: source path escapes package") from exc
        if not source_path.is_file():
            raise ValueError(f"{relative}: pinned source bytes are missing")
        actual = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual != publication[1]:
            raise ValueError(f"{relative}: sha256 differs from sources.law")
    return metadata["formalizationDepthReason"].strip()


def measure_act(boundaries, act: str) -> tuple[dict[str, int] | None, str]:
    """Глубина ОДНОГО акта — либо `None` и причина, по которой мера к нему
    неприменима.

    Отдельный вход, а не тело цикла: тот же вопрос задаёт
    `corpus/tools/checks/doctor.py`, и своим разбором границ он разошёлся бы с
    воротами молча — тот же класс дефекта, ради которого сама мера
    импортируется из скилла, а не переписывается здесь.
    """
    source = boundaries.act_source(act)
    # Обычные пакеты сохраняют исходный приоритет причин: source, CLIR, .law.
    # Только явный marker позволяет обработать пакет без conventional ru.txt.
    if source is None:
        try:
            not_applicable_reason = declared_non_applicable_reason(boundaries, act)
        except (OSError, ValueError) as exc:
            return None, f"{INVALID_MARKER_PREFIX}{exc}"
        if not_applicable_reason is None:
            return None, NO_SOURCE
        if not boundaries.act_clirs(act):
            return None, NO_CLIR
        if not boundaries.act_laws(act):
            return None, NO_LAWS
        return None, NOT_APPLICABLE_PREFIX + not_applicable_reason
    clirs = boundaries.act_clirs(act)
    if not clirs:
        return None, NO_CLIR
    if not boundaries.act_laws(act):
        return None, NO_LAWS
    try:
        not_applicable_reason = declared_non_applicable_reason(boundaries, act)
    except (OSError, ValueError) as exc:
        return None, f"{INVALID_MARKER_PREFIX}{exc}"
    if not_applicable_reason is not None:
        return None, NOT_APPLICABLE_PREFIX + not_applicable_reason
    try:
        composite_path = composite_depth_path(boundaries, act)
        if composite_path is not None:
            return composite_counts(boundaries, act, clirs, composite_path), ""
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return None, f"{INVALID_MARKER_PREFIX}{exc}"
    rows = boundaries.depth(source, clirs)["rows"]
    if not rows:
        # Акт без заголовков «Статья N» — мера неприменима, а не нулевая.
        return None, NO_UNIT
    declaration = boundaries.act_declaration(act)
    declared: set[str] = set()
    if declaration is not None:
        payload = json.loads(declaration.read_text(encoding="utf-8"))
        # Форма `{"editions": [...]}`: границы объявляются У КАЖДОЙ редакции, и
        # верхнего уровня у такого файла нет вовсе. Прежде читался только он —
        # то есть у акта в этой форме КАЖДАЯ объявленная граница была для
        # храповика невидима, и все её SOURCE_ONLY считались необъяснёнными.
        # Третий случай одной слепоты: так же не читались `unit` (мера глубины)
        # и `scope` (учёт статей до DECISION-0026). Берётся объединение
        # редакций: мера считает статьи ОДНОГО документа, но какого именно —
        # решает `act_source`, и сузить объединение здесь значило бы разойтись
        # с ним ещё одним соглашением.
        sources = [payload] + list(payload.get("editions", []))
        for entry in sources:
            declared |= set(pinning().declared_articles(entry)[0])
    counts = {level: 0 for level in RATCHET}
    counts["—"] = 0
    for row in rows:
        counts[row["level"]] += 1
        if row["level"] == "SOURCE_ONLY" and row["article"] not in declared:
            counts["UNEXPLAINED"] += 1
    return counts, ""


def measure() -> dict[str, dict[str, int]]:
    """Слепок глубины по актам, у которых мера применима."""
    boundaries = load_measure()
    out: dict[str, dict[str, int]] = {}
    for act in boundaries.known_acts():
        counts, why = measure_act(boundaries, act)
        if why.startswith(INVALID_MARKER_PREFIX):
            sys.exit(f"FAIL {act}: {why}")
        if counts is not None:
            out[act] = counts
    return out


def settled_acts() -> set[str] | None:
    """Акты, чьё дерево УЛЕЖАЛОСЬ: под git и без незакоммиченных правок.
    `None` — git недоступен, и тогда обязанность регистрации не вменяется
    никому.

    Различение нужно ровно по той же причине, что и в `verify/ci/gates/repo/check_gate_wiring.py`
    (`tracked_names`): по репозиторию одновременно работают десятки сессий, и
    акт в активной правке отдаёт мере ДВИЖУЩЕЕСЯ число. Заморозив его, эти
    ворота зафиксировали бы чужой промежуточный замер — тот самый вред, из-за
    которого `--write` назван опасным. Поэтому неулежавшийся акт не роняет
    прогон, но и не молчит: он назван строкой отчёта."""
    import subprocess  # noqa: PLC0415 — только на этом пути, gate иначе чист
    laws = "corpus/laws"
    try:
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", f"{laws}/**/law.toml"],
            capture_output=True, text=True, check=True).stdout
        dirty = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain", "--", laws],
            capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None

    def act_of(path: str) -> str:
        rest = path.split(f"{laws}/", 1)[-1]
        return "-".join(Path(rest).parent.parts)

    settled = {act_of(line) for line in tracked.splitlines() if line}
    for line in dirty.splitlines():
        path = line[3:].strip().strip('"')
        if not path.startswith(f"{laws}/"):
            continue
        rest = path.split(f"{laws}/", 1)[-1].split("/")
        # Правка ЛЮБОГО файла под каталогом акта делает его неулежавшимся;
        # имя акта — самый длинный префикс пути, который есть среди актов.
        for cut in range(len(rest), 0, -1):
            settled.discard("-".join(rest[:cut]))
    return settled


def register(act: str) -> int:
    """Вписать ОДИН акт в базу, не трогая остальные.

    Отдельный вход, потому что `--write` перезамораживает базу ЦЕЛИКОМ —
    снимок ВСЕХ актов на текущий момент, — и на живом дереве это фиксирует
    чужие промежуточные значения (наблюдалось 29.08.2026: три акта пропали из
    меры между чтением и записью). Регистрация одного акта такого права не
    требует и его не берёт: читается существующий JSON, меняется один ключ."""
    boundaries = load_measure()
    # Адресный вход не должен обходить весь корпус ради проверки одного имени:
    # known_acts() перечисляет доманифестные каталоги и на крупном дереве
    # задерживает --register до самого замера. act_dir разрешает то же имя
    # непосредственно, а неприменимый каталог отсеет measure_act ниже.
    if boundaries.act_dir(act) is None:
        print(f"{act}: такого акта в corpus/laws нет", file=sys.stderr)
        return 1
    counts, why = measure_act(boundaries, act)
    if counts is None:
        print(f"{act}: мера неприменима — {why}. В базу такой акт не "
              f"вписывается вовсе: `main()` объявляет регрессом всё, что есть "
              f"в базе и чего нет в измерении", file=sys.stderr)
        return 1
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    was = base.get(act)
    base[act] = counts
    BASELINE.write_text(
        json.dumps(base, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(f"{act} вписан в базу глубины: {counts}"
          + (f" (было {was})" if was is not None else ""))
    return 0


def compare(current: dict[str, dict[str, int]], base: dict[str, dict[str, int]],
            settled: set[str] | None) -> tuple[list[str], list[str], list[str]]:
    """Сверка замера с базой: (отказы, прогресс, заметки).

    Отдельный вход, а не тело `main()`, ради канарейки: полный замер стоит
    ~20 с на корпусе, и прогонять его по разу на мутацию значило бы платить
    минуту за то, что сравнение — чистая функция от двух словарей."""
    problems: list[str] = []
    progress: list[str] = []
    notes: list[str] = []
    for act, counts in sorted(current.items()):
        if act not in base:
            # До 29.08.2026 эта ветка печаталась как ПРОГРЕСС — зелёной
            # строкой «новый акт под мерой». Прочитывалось это как «акт
            # измерен», а означало ровно обратное: пока ключа в базе нет,
            # храповик по нему не работает, и просесть акт может на любую
            # глубину молча. Защиты от забывчивости не было никакой: реестр
            # ведётся руками, а напоминание выглядело поздравлением.
            if settled is not None and act not in settled:
                notes.append(f"{act}: измеряется ({counts}), в базе нет — но "
                             f"дерево акта в правке, число ещё движется. "
                             f"Обязанность вписать возникнет, когда правки "
                             f"улягутся")
            else:
                problems.append(
                    f"{act}: мера его отдаёт ({counts}), а в базе ключа нет — "
                    f"храповик по этому акту не работает. Впишите одним "
                    f"действием: python3 verify/ci/gates/coverage/check_formalization_depth.py "
                    f"--register {act}")
            continue
        for level, direction in RATCHET.items():
            was, now = base[act].get(level, 0), counts.get(level, 0)
            if now == was:
                continue
            moved_well = (now - was) * direction > 0
            line = f"{act}: {level} {was} → {now}"
            (progress if moved_well else problems).append(line)
    for act in sorted(set(base) - set(current)):
        problems.append(f"{act}: акт пропал из меры (был {base[act]})")
    return problems, progress, notes


def canary(current: dict[str, dict[str, int]],
           base: dict[str, dict[str, int]]) -> int:
    """Каждое из трёх утверждений храповика обязано падать на своей мутации.

    Мутируется КОПИЯ базы в памяти: файл базы общий, а по репозиторию идут
    десятки сессий — запись-с-восстановлением в него была бы гонкой."""
    victim = next((a for a in sorted(current) if a in base), None)
    if victim is None:
        print("canary: база и замер не пересекаются — мутировать нечего",
              file=sys.stderr)
        return 1
    settled = {victim}

    dropped = {k: v for k, v in base.items() if k != victim}
    sank = dict(base)
    sank[victim] = dict(base[victim], EXECUTABLE=base[victim].get("EXECUTABLE", 0) + 1)
    vanished = dict(base) | {"акт-которого-нет": {"EXECUTABLE": 1}}

    cases = (
        ("акт вне базы", dropped,
         lambda found: any("в базе ключа нет" in line for line in found)),
        ("просадка уровня", sank,
         lambda found: any(f"{victim}: EXECUTABLE" in line for line in found)),
        ("акт пропал из меры", vanished,
         lambda found: any("пропал из меры" in line for line in found)),
    )
    for what, mutated, caught in cases:
        problems, _, _ = compare(current, mutated, settled)
        if not caught(problems):
            print(f"canary: мутация «{what}» не поймана — эта треть храповика "
                  f"не работает", file=sys.stderr)
            return 1
    print(f"check_formalization_depth: канарейка держит {len(cases)} мутации "
          f"— акт вне базы, просадка уровня, исчезновение из меры")
    return 0


def rename(old: str, new: str) -> int:
    """Переименовать ОДИН ключ базы, не пересчитывая меру.

    Нужно для переезда каталогов: база ключуется ИМЕНЕМ акта, а имя есть путь
    от `corpus/laws` с «/»→«-» (§10, DECISION-0033 §6.1). Сгруппируй корпус —
    и 92 ключа сменятся разом, хотя ни одна статья не изменилась. Без этого
    входа мера прочтёт переезд как двойную катастрофу: «92 акта пропали из
    меры» плюс «92 акта измеряются, а в базе их нет».

    Мера НЕ пересчитывается намеренно. Переезд каталога глубину не меняет, и
    пересчёт здесь означал бы заморозку СЕГОДНЯШНЕГО значения вместо того,
    которое храповик держал до переезда, — то есть тихую перезаморозку под
    видом переименования. Числа переносятся как есть; если они и правда
    сдвинулись, это увидит следующий обычный прогон."""
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    if old not in base:
        near = [k for k in sorted(base) if k.endswith(old) or old.endswith(k)]
        print(f"{old}: такого ключа в базе нет"
              + (f" (похожие: {', '.join(near[:3])})" if near else ""),
              file=sys.stderr)
        return 1
    if new in base:
        print(f"{new}: ключ уже есть — переименование затёрло бы его значение "
              f"{base[new]}. Разберитесь, какой из двух верен, и уберите "
              f"лишний осознанным действием", file=sys.stderr)
        return 1
    # Опечатка в НОВОМ имени иначе прошла бы молча и всплыла на следующем
    # прогоне как «акт пропал из меры» — то есть виной выглядел бы переезд.
    boundaries = load_measure()
    if new not in boundaries.known_acts():
        print(f"{new}: акта с таким именем в corpus/laws нет — имя акта есть "
              f"путь от corpus/laws с «/»→«-» (kz/laws/osms → kz-osms)",
              file=sys.stderr)
        return 1
    base[new] = base.pop(old)
    BASELINE.write_text(
        json.dumps(base, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(f"{old} → {new}: ключ перенесён, значение {base[new]} не пересчитано")
    return 0


def only(act: str) -> int:
    """Точечная сверка ОДНОГО акта против ЕГО ключа базы.

    Заведён 30.08.2026 ретро-аудитом теневого протокола formalize-act: полный
    замер стоит минуты и в общем дереве красен чужими движущимися актами, а
    сессия спрашивает про СВОЙ. Меряется один акт (секунды, `measure_act` — та
    же мера, что у `--register` и доктора), сверка — той же `compare` на
    усечённых словарях. Ответ СТРОГИЙ: правовой акт не в базе — отказ, даже если его
    дерево в правке (спрашивающий и есть правящая сессия — оговорка про
    неулежавшееся дерево здесь укрывала бы спрашивающего от его же вопроса).
    Явная инженерная методика без правовой единицы — проверяемый
    NOT_APPLICABLE; существующий ключ базы маркером не обходится. Чужие
    акты, включая пропавшие из меры, видит только тотальный прогон."""
    boundaries = load_measure()
    # --only спрашивает ровно один акт; глобальный known_acts() здесь даёт
    # тот же ответ лишь после дорогостоящего обхода всех каталогов.
    if boundaries.act_dir(act) is None:
        print(f"{act}: такого акта в corpus/laws нет (имя — путь от "
              f"corpus/laws с «/»→«-», например kz-kun-1920)", file=sys.stderr)
        return 1
    if not BASELINE.exists():
        print(f"нет {BASELINE.relative_to(ROOT)} — запустите с --write",
              file=sys.stderr)
        return 1
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    counts, why = measure_act(boundaries, act)
    if counts is None:
        if why.startswith(NOT_APPLICABLE_PREFIX):
            if act in base:
                print(f"FAIL {act}: в базе {base[act]}, а пакет объявлен "
                      "NOT_APPLICABLE; действующую строку храповика нельзя "
                      "обойти маркером", file=sys.stderr)
                return 1
            print(f"NOT_APPLICABLE {act}: правовая мера §33.1 не применяется; "
                  f"source, CLIR и собственные .law найдены. Причина: "
                  f"{why[len(NOT_APPLICABLE_PREFIX):]}")
            return 0
        if act in base:
            print(f"FAIL {act}: в базе {base[act]}, а мера стала неприменима — "
                  f"{why}", file=sys.stderr)
        else:
            print(f"{act}: мера неприменима ({why}) и ключа в базе нет — "
                  f"сверять нечего", file=sys.stderr)
        return 1
    problems, progress, _ = compare(
        {act: counts}, {act: base[act]} if act in base else {}, settled=None)
    if problems:
        for line in problems:
            print(f"FAIL {line}", file=sys.stderr)
        return 1
    for line in progress:
        print(f"  глубина выросла — {line}")
    print(f"check_formalization_depth --only {act}: {counts} — сходится с "
          f"базой (остальной корпус — только тотальным прогоном)")
    return 0


def main() -> int:
    if "--only" in sys.argv:
        index = sys.argv.index("--only")
        if index + 1 >= len(sys.argv):
            print("--only требует имя акта", file=sys.stderr)
            return 1
        return only(sys.argv[index + 1])

    if "--rename" in sys.argv:
        index = sys.argv.index("--rename")
        if index + 2 >= len(sys.argv):
            print("--rename требует два имени: старое и новое", file=sys.stderr)
            return 1
        return rename(sys.argv[index + 1], sys.argv[index + 2])

    if "--register" in sys.argv:
        index = sys.argv.index("--register")
        if index + 1 >= len(sys.argv):
            print("--register требует имя акта", file=sys.stderr)
            return 1
        return register(sys.argv[index + 1])

    current = measure()
    if "--write" in sys.argv:
        # Полная перезаморозка на живом дереве фиксирует ЧУЖИЕ промежуточные
        # значения (29.08.2026: три акта пропали из меры между чтением и
        # записью — соседняя сессия правила их в этот момент). Поэтому
        # `--write` отказывает, пока `corpus/laws` И `corpus/clir` не чисты —
        # мера читает ОБА (закреплённые байты и CLIR), и фильтр «только акты
        # под мерой» здесь недостаточен: акт, неизмеримый в момент чтения,
        # становится измеримым за время записи. Точечные входы (`--register`,
        # `--rename`) этого права не требуют (DECISION-0062).
        import subprocess  # noqa: PLC0415 — только на этом пути
        try:
            dirty = subprocess.run(
                ["git", "-C", str(ROOT), "status", "--porcelain", "--",
                 "corpus/laws", "corpus/clir"],
                capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            dirty = None
        if dirty is None:
            print("--write: git недоступен — чистоту corpus/laws и "
                  "corpus/clir не проверить, а перезаморозка живого дерева "
                  "фиксирует чужой mid-edit. Отказ", file=sys.stderr)
            return 1
        if dirty.strip():
            moved = [line[3:].strip() for line in dirty.splitlines()][:4]
            print(f"--write: дерево не улежалось — в правке "
                  f"{len(dirty.splitlines())} путей под мерой "
                  f"({', '.join(moved)}…). Перезаморозка сейчас зафиксировала "
                  f"бы движущиеся числа как базу (замер 29.08.2026: три акта "
                  f"пропали из меры между чтением и записью). Дождитесь "
                  f"чистого дерева либо впишите свой акт точечно: "
                  f"--register <акт>", file=sys.stderr)
            return 1
        BASELINE.write_text(
            json.dumps(current, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        print(f"база глубины перезаморожена: {len(current)} актов")
        return 0
    if not BASELINE.exists():
        sys.exit(f"нет {BASELINE.relative_to(ROOT)} — запустите с --write")
    base = json.loads(BASELINE.read_text(encoding="utf-8"))

    if "--canary" in sys.argv:
        return canary(current, base)

    problems, progress, notes = compare(current, base, settled_acts())

    for line in progress:
        print(f"  глубина выросла — {line}")
    for line in notes:
        print(f"  NOTE {line}")
    if problems:
        print("check_formalization_depth: РЕГРЕСС ГЛУБИНЫ", file=sys.stderr)
        for line in problems:
            print(f"  {line}", file=sys.stderr)
        print("  если сдвиг намеренный — перезаморозьте базу "
              "`--write` ОТДЕЛЬНЫМ коммитом с обоснованием", file=sys.stderr)
        return 1
    total = {level: sum(c.get(level, 0) for c in current.values()) for level in RATCHET}
    print(f"check_formalization_depth: {len(current)} актов под мерой, "
          f"EXECUTABLE {total['EXECUTABLE']}, ANCHORED {total['ANCHORED']}, "
          f"SOURCE_ONLY {total['SOURCE_ONLY']} — регресса нет")
    return 0


if __name__ == "__main__":
    # Строгий argv (DECISION-0073): неизвестный флаг — громкий отказ,
    # а не молчаливый полный прогон; --help печатает шапку файла.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
    from gate_argv import guard_argv
    guard_argv({"--only": 1, "--rename": 2, "--register": 1, "--write": 0, "--canary": 0})
    sys.exit(main())
